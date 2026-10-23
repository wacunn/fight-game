"""
Toronto brawler RL environment, written in JAX (jit + vmap over thousands of envs).

Design goal: the agent trains in the *same* city under the *same* rules it plays in.
  * Map: ai_grid.js, rasterized from the game's own collision (tools/export_ai_grid.js).
  * Rules copied from game.js: player speeds (7 / 11.5 sprint), JAB & KICK range/cone/damage/
    cooldown/knockback, glory kill on a staggered foe (<=32% HP, within 4 m), robot chase/punch
    timing (trigger 2.2 m, land at mid-swing if <=2.4 m, cooldown 1.1/mult + U(0,.4)), armor
    absorbing 65%, snatchers disguised until within 10 m or hit, civilians fleeing, berserk
    (rage 100 -> 16 s, x3 damage, x2.2 knockback, civilians shoved aside, not hurt), peace
    sanctuary (no fighting, NPCs stand down, +8 HP/s, +5 armor/s), mission crate completed by an
    attack within 6.5 m (+1500 score, +40 HP) guarded by 3 sentries, difficulty multipliers.
  * Observation is EGOCENTRIC ONLY - no absolute position (see OBS_SPEC.md). The agent gets the
    goal as range+bearing (like the in-game mission arrow) and must build its own map of the city.

Training-only extras (never seen by the policy, used for shaping / auxiliary losses / probes):
  geodesic distance and shortest-path direction to the goal, a 144 m egocentric "cognitive map"
  target, absolute position.
"""
from typing import NamedTuple

import jax
import jax.numpy as jnp
import numpy as np

# ----------------------------------------------------------------------------- constants
DT = 0.1                       # 10 Hz decisions (copilot runs at the same rate in-game)
EYE = 1.7                      # camera height: the game's hit tests are 3D from the eye
WALK, SPRINT = 7.0, 11.5
N_AMBIENT, N_GUARD = 32, 3
N_NPC = N_AMBIENT + N_GUARD
K_OBS = 6                      # nearest NPCs observed
NPC_RANGE = 40.0
PATCH, PATCH_CELL, PATCH_ROW0 = 16, 2.0, 11.5     # 16x16 @ 2 m: 23 m ahead .. 7 m behind, +-15 m sideways
MAP, MAP_CELL = 24, 6.0                           # 24x24 @ 6 m: 144 m window (aux target only)
TURNS = jnp.array([-0.5, -0.15, 0.0, 0.15, 0.5])  # rad per decision, positive = turn RIGHT (yaw -= d)
N_MOVE, N_TURN, N_ATK = 6, 5, 3                   # move: none,fwd,back,left,right,sprint-fwd ; atk: none,primary,kick
ACT_DIMS = (N_MOVE, N_TURN, N_ATK)
NPC_FEATS = 13                 # per observed NPC (obs_version 2: +fine distance, +jab-reach, +kick-reach)
VEC_DIM = 33 + K_OBS * NPC_FEATS   # 111
PRIV_DIM = 6
FACING_COS = 0.50              # melee cone: horizontal facing +-60 deg (cos > 0.50)

# attacks (game.js ATTACKS)
JAB = dict(damage=30.0, range=3.5, cooldown=0.22, kb=6.0)
KICK = dict(damage=100.0, range=4.2, cooldown=0.55, kb=32.0)
GLORY_CD = 0.5
KB_DISP = 0.119                # knockback velocity decays 0.86/frame @60 fps -> displacement ~ kb*0.119

# difficulty table (easy, medium, hard, impossible)
DIFF = dict(
    civ=jnp.array([0.75, 0.50, 0.25, 0.10]), rob=jnp.array([0.18, 0.35, 0.50, 0.55]),
    hp=jnp.array([0.85, 1.0, 1.35, 1.75]), spd=jnp.array([0.9, 1.0, 1.15, 1.35]),
    dmg=jnp.array([0.7, 1.0, 1.4, 1.9]), cdm=jnp.array([1.3, 1.0, 0.8, 0.6]),
    aggro=jnp.array([28.0, 35.0, 48.0, 65.0]))
DIFF_P = jnp.array([0.3, 0.4, 0.25, 0.05])

# archetypes [kind][arch]: hp, speed, damage   (kind 0 civilian, 1 robot, 2 snatcher)
ARCH_HP = jnp.array([[60, 55, 70, 55], [145, 180, 115, 135], [160, 140, 175, 160]], jnp.float32)
ARCH_SPD = jnp.array([[2.6, 2.8, 3.2, 2.7], [3.6, 3.1, 4.4, 3.9], [4.0, 4.3, 3.8, 4.0]], jnp.float32)
ARCH_DMG = jnp.array([[0, 0, 0, 0], [18, 24, 15, 20], [22, 19, 25, 22]], jnp.float32)


# ----------------------------------------------------------------------------- world pytree
class World(NamedTuple):
    occ: jnp.ndarray        # (H, W) uint8, 1 = blocked
    pool6: jnp.ndarray      # (H6, W6) float16
    fields: jnp.ndarray     # (G, H2, W2) float16 geodesic metres
    goals: jnp.ndarray      # (G, 2)
    spawn_xz: jnp.ndarray   # (S, 2)
    x0: jnp.ndarray
    z0: jnp.ndarray
    peace: jnp.ndarray      # (3,) x, z, radius


def make_world(w):
    m = w["meta"]
    pz = m["peaceZone"]
    return World(occ=jnp.asarray(w["occ"]), pool6=jnp.asarray(w["pool6"]), fields=jnp.asarray(w["fields"]),
                 goals=jnp.asarray(w["goals"]), spawn_xz=jnp.asarray(w["spawn_xz"]),
                 x0=jnp.float32(m["x0"]), z0=jnp.float32(m["z0"]),
                 peace=jnp.array([pz["x"], pz["z"], pz["radius"]], jnp.float32))


class NPC(NamedTuple):
    alive: jnp.ndarray; respawn_t: jnp.ndarray; kind: jnp.ndarray; unmasked: jnp.ndarray
    x: jnp.ndarray; z: jnp.ndarray; hp: jnp.ndarray; maxhp: jnp.ndarray; speed: jnp.ndarray
    dmg: jnp.ndarray; cd: jnp.ndarray; atk_t: jnp.ndarray; prog: jnp.ndarray; stag_t: jnp.ndarray
    flee_t: jnp.ndarray; wander_a: jnp.ndarray; wander_t: jnp.ndarray; aggro: jnp.ndarray; guard: jnp.ndarray


class State(NamedTuple):
    t: jnp.ndarray; max_t: jnp.ndarray
    pos: jnp.ndarray; yaw: jnp.ndarray; pos0: jnp.ndarray
    health: jnp.ndarray; armor: jnp.ndarray; rage: jnp.ndarray; berserk_t: jnp.ndarray; atk_cd: jnp.ndarray
    score: jnp.ndarray; diff: jnp.ndarray
    goal: jnp.ndarray; goal_xy: jnp.ndarray; geo0: jnp.ndarray; phi: jnp.ndarray
    prev_act: jnp.ndarray
    npc: NPC
    ep_ret: jnp.ndarray; kills: jnp.ndarray; civ_hits: jnp.ndarray; dmg_taken: jnp.ndarray
    ktar: jnp.ndarray              # fighter: hostile KOs needed to win this episode (1..4); runner: 0


class Curriculum(NamedTuple):
    lo: jnp.ndarray         # geodesic start-goal band (m)
    hi: jnp.ndarray
    p_uniform: jnp.ndarray  # fraction of episodes with distance uniform in [10, hi]
    stage: jnp.ndarray      # fighter curriculum stage 0..3 (ignored by the runner)


# ----------------------------------------------------------------------------- geometry helpers
def fwd_right(yaw):
    s, c = jnp.sin(yaw), jnp.cos(yaw)
    return jnp.stack([-s, -c], -1), jnp.stack([c, -s], -1)


def blocked(world, x, z):
    i = jnp.floor(z - world.z0).astype(jnp.int32)
    j = jnp.floor(x - world.x0).astype(jnp.int32)
    H, W = world.occ.shape
    inb = (i >= 0) & (i < H) & (j >= 0) & (j < W)
    return jnp.where(inb, world.occ[jnp.clip(i, 0, H - 1), jnp.clip(j, 0, W - 1)] > 0, True)


def in_peace(world, x, z):
    return (x - world.peace[0]) ** 2 + (z - world.peace[1]) ** 2 <= world.peace[2] ** 2


def geo_dist(world, g, x, z):
    """Bilinear geodesic distance on the 2 m planner grid, ignoring unreachable corners."""
    _, H2, W2 = world.fields.shape
    u = (x - world.x0) / 2.0 - 0.5
    v = (z - world.z0) / 2.0 - 0.5
    j0 = jnp.floor(u).astype(jnp.int32); i0 = jnp.floor(v).astype(jnp.int32)
    fu = u - j0; fv = v - i0
    tot = 0.0; wsum = 0.0
    for di, dj, w in ((0, 0, (1 - fu) * (1 - fv)), (0, 1, fu * (1 - fv)), (1, 0, (1 - fu) * fv), (1, 1, fu * fv)):
        ii = jnp.clip(i0 + di, 0, H2 - 1); jj = jnp.clip(j0 + dj, 0, W2 - 1)
        val = world.fields[g, ii, jj].astype(jnp.float32)   # single gather (no slice copy under vmap)
        ok = jnp.isfinite(val)
        tot = tot + jnp.where(ok, w * val, 0.0); wsum = wsum + jnp.where(ok, w, 0.0)
    eu = jnp.hypot(world.goals[g, 0] - x, world.goals[g, 1] - z)
    return jnp.where(wsum > 1e-4, tot / jnp.maximum(wsum, 1e-4), 1.5 * eu + 50.0)


def geo_dir_ego(world, g, x, z, yaw):
    """Shortest-path direction to the goal, in the agent's frame (ahead, right)."""
    gx = geo_dist(world, g, x + 1.0, z) - geo_dist(world, g, x - 1.0, z)
    gz = geo_dist(world, g, x, z + 1.0) - geo_dist(world, g, x, z - 1.0)
    d = -jnp.stack([gx, gz]); d = d / (jnp.linalg.norm(d) + 1e-6)
    f, r = fwd_right(yaw)
    return jnp.stack([d @ f, d @ r])


def ego_samples(pos, yaw, n, cell, row0):
    f, r = fwd_right(yaw)
    ii = jnp.arange(n, dtype=jnp.float32)
    ahead = (row0 - ii) * cell                     # row 0 = farthest ahead
    right = (ii - (n - 1) / 2.0) * cell            # col 0 = leftmost
    A, R = jnp.meshgrid(ahead, right, indexing="ij")
    return pos[0] + A * f[0] + R * r[0], pos[1] + A * f[1] + R * r[1]


def patch_obs(world, pos, yaw):
    X, Z = ego_samples(pos, yaw, PATCH, PATCH_CELL, PATCH_ROW0)
    return blocked(world, X, Z).astype(jnp.float32)


def map_target(world, pos, yaw):
    X, Z = ego_samples(pos, yaw, MAP, MAP_CELL, (MAP - 1) / 2.0)
    H6, W6 = world.pool6.shape
    i = jnp.floor((Z - world.z0) / 6.0).astype(jnp.int32); j = jnp.floor((X - world.x0) / 6.0).astype(jnp.int32)
    inb = (i >= 0) & (i < H6) & (j >= 0) & (j < W6)
    return jnp.where(inb, world.pool6[jnp.clip(i, 0, H6 - 1), jnp.clip(j, 0, W6 - 1)].astype(jnp.float32), 1.0)


def range_bearing(pos, yaw, tx, tz):
    f, r = fwd_right(yaw)
    d = jnp.stack([tx - pos[0], tz - pos[1]])
    a, b = d @ f, d @ r
    dist = jnp.hypot(a, b)
    ang = jnp.arctan2(b, a)                        # 0 = straight ahead, +pi/2 = to the right
    return jnp.sin(ang), jnp.cos(ang), dist


# ----------------------------------------------------------------------------- NPC spawning
def _ring_spot(world, key, cx, cz, rmin, rmax, avoid_x, avoid_z, min_gap, tries=8):
    """First of `tries` random points in an annulus that is walkable, outside the sanctuary
    buffer and at least min_gap from (avoid_x, avoid_z). Returns (ok, x, z).
    When the ring is centred on the player, pass min_gap=0 (rmin already keeps the gap): a 24 m gap
    here previously made every spawn within 24 m of the player silently fail."""
    k1, k2 = jax.random.split(key)
    a = jax.random.uniform(k1, (tries,), maxval=2 * jnp.pi)
    rr = jnp.sqrt(jax.random.uniform(k2, (tries,), minval=rmin ** 2, maxval=rmax ** 2))
    x = cx + rr * jnp.cos(a); z = cz + rr * jnp.sin(a)
    pdist = jnp.hypot(x - world.peace[0], z - world.peace[1])
    ok = (~blocked(world, x, z)) & (pdist >= world.peace[2] + 15.0) & (jnp.hypot(x - avoid_x, z - avoid_z) >= min_gap)
    k = jnp.argmax(ok)
    return ok.any(), x[k], z[k]


def _new_npc_stats(key, diff, kind, guard):
    ka, kw = jax.random.split(key)
    arch = jax.random.randint(ka, (), 0, 4)
    arch = jnp.where(guard, 1 + jax.random.randint(ka, (), 0, 3), arch)
    civ = kind == 0
    hp = ARCH_HP[kind, arch] * jnp.where(civ, 1.0, DIFF["hp"][diff]) * jnp.where(guard, 1.25, 1.0)
    spd = ARCH_SPD[kind, arch] * jnp.where(civ, 1.0, DIFF["spd"][diff]) * jnp.where(guard, 1.1, 1.0)
    dmg = ARCH_DMG[kind, arch] * DIFF["dmg"][diff] * jnp.where(guard, 1.2, 1.0)
    cd = 1.1 / DIFF["cdm"][diff]
    aggro = jnp.where(guard, 42.0, jnp.where(civ, 0.0, DIFF["aggro"][diff]))
    return hp, spd, jnp.round(dmg), cd, aggro, jax.random.uniform(kw, (), maxval=2 * jnp.pi)


def _spawn_slot(world, key, npc, i, diff, px, pz, rmin, rmax, force_kind=-1, tries=8):
    """(Re)spawn ambient slot i in a ring around the player. force_kind: -1 = sample the difficulty's
    population mix, 0 = civilian, 1 = robot."""
    k1, k2, k3, k4 = jax.random.split(key, 4)
    ok, x, z = _ring_spot(world, k1, px, pz, rmin, rmax, px, pz, 0.0, tries=tries)
    u = jax.random.uniform(k2)
    rand_kind = jnp.where(u < DIFF["civ"][diff], 0, jnp.where(u < DIFF["civ"][diff] + DIFF["rob"][diff], 1, 2))
    kind = jnp.where(force_kind >= 0, force_kind, rand_kind)
    hp, spd, dmg, cd, aggro, wa = _new_npc_stats(k3, diff, kind, False)
    upd = lambda arr, v: arr.at[i].set(jnp.where(ok, v, arr[i]))
    return npc._replace(
        alive=upd(npc.alive, True), respawn_t=npc.respawn_t.at[i].set(jnp.where(ok, 0.0, 0.5)),
        kind=upd(npc.kind, kind), unmasked=upd(npc.unmasked, False), x=upd(npc.x, x), z=upd(npc.z, z),
        hp=upd(npc.hp, hp), maxhp=upd(npc.maxhp, hp), speed=upd(npc.speed, spd), dmg=upd(npc.dmg, dmg),
        cd=upd(npc.cd, cd), atk_t=upd(npc.atk_t, 0.5 + 0.5 * jax.random.uniform(k4)), prog=upd(npc.prog, -1.0),
        stag_t=upd(npc.stag_t, 0.0), flee_t=upd(npc.flee_t, 0.0), wander_a=upd(npc.wander_a, wa),
        wander_t=upd(npc.wander_t, 3.0), aggro=upd(npc.aggro, aggro), guard=npc.guard.at[i].set(False))


def _empty_npcs():
    z = jnp.zeros(N_NPC, jnp.float32)
    return NPC(alive=jnp.zeros(N_NPC, bool), respawn_t=z, kind=jnp.zeros(N_NPC, jnp.int32),
               unmasked=jnp.zeros(N_NPC, bool), x=z, z=z, hp=z, maxhp=jnp.ones(N_NPC), speed=z, dmg=z,
               cd=jnp.ones(N_NPC), atk_t=z, prog=-jnp.ones(N_NPC), stag_t=z, flee_t=z, wander_a=z,
               wander_t=z, aggro=z, guard=jnp.zeros(N_NPC, bool))


def hostile_mask(n):
    """NPCs that visibly are fighters (robots, unmasked snatchers) - what the policy can tell apart."""
    return n.alive & ((n.kind == 1) | ((n.kind == 2) & n.unmasked))


def fighter_phi(world, pos, health, n):
    """Brawler shaping potential. Healthy: -dist to nearest visible hostile (capped 30 m) / 5, so closing
    1 m pays +0.2. Low health (<35): -dist to the sanctuary / 10. Potential-based, so it cannot change
    which policy is optimal; it only makes 'go engage' discoverable."""
    d = jnp.hypot(n.x - pos[0], n.z - pos[1])
    dh = jnp.min(jnp.where(hostile_mask(n), d, 30.0))
    dh = jnp.minimum(dh, 30.0)
    dp = jnp.minimum(jnp.hypot(world.peace[0] - pos[0], world.peace[1] - pos[1]), 300.0)
    return jnp.where(health < 35.0, -dp / 10.0, -dh / 5.0)


# fighter curriculum stages:      0: duel   1: 2v1 + civ   2: 3v1 + 2 civs   3: normal city
FIGHT_N_HOST = jnp.array([1, 2, 3, 0])
FIGHT_N_CIV = jnp.array([0, 1, 2, 0])
FIGHT_KTAR = jnp.array([1.0, 2.0, 3.0, 4.0])
FIGHT_MAX_T = jnp.array([500, 700, 900, 1500])


# ----------------------------------------------------------------------------- reset
def reset(world, key, cur: Curriculum, fighter: bool = False):
    ks = jax.random.split(key, 10)
    G = world.goals.shape[0]
    diff = jax.random.choice(ks[0], 4, p=DIFF_P)
    g = jax.random.randint(ks[1], (), 0, G)
    # start position: geodesic distance to the goal inside the curriculum band
    cand = world.spawn_xz[jax.random.randint(ks[2], (128,), 0, world.spawn_xz.shape[0])]
    gd = jax.vmap(lambda p: geo_dist(world, g, p[0], p[1]))(cand)
    uni = jax.random.uniform(ks[3]) < cur.p_uniform
    lo = jnp.where(uni, 10.0, cur.lo)
    ok = (gd >= lo) & (gd <= cur.hi) & ~in_peace(world, cand[:, 0], cand[:, 1])
    pri = jax.random.uniform(ks[4], (128,)) + ok * 2.0
    k = jnp.where(ok.any(), jnp.argmax(pri), jnp.argmin(jnp.abs(gd - cur.hi)))
    pos = cand[k]; geo0 = gd[k]
    yaw = jax.random.uniform(ks[5], minval=-jnp.pi, maxval=jnp.pi)

    if fighter:
        # 30% of episodes replay an earlier stage so old skills are not forgotten
        cs = jnp.clip(cur.stage.astype(jnp.int32), 0, 3)
        stage = jnp.where(jax.random.uniform(ks[8]) < 0.3, jax.random.randint(ks[9], (), 0, cs + 1), cs)
        diff = jnp.where(stage == 0, 0, jnp.where(stage == 1, jnp.minimum(diff, 1), diff))
        n_host, n_civ = FIGHT_N_HOST[stage], FIGHT_N_CIV[stage]
        n_near = jnp.where(stage == 3, 2, 0)          # random-kind close slots only in the full city
        ring_lo = jnp.where(stage == 0, 2.5, 3.0); ring_hi = jnp.where(stage == 0, 6.0, 9.0)
        ktar = FIGHT_KTAR[stage]
        max_t = FIGHT_MAX_T[stage].astype(jnp.int32)
    else:
        n_host, n_civ, n_near = jnp.int32(0), jnp.int32(0), jnp.int32(2)
        ring_lo, ring_hi = jnp.float32(3.0), jnp.float32(9.0)
        ktar = jnp.float32(0.0)
        max_t = jnp.minimum(jnp.ceil(1.6 * geo0 / (WALK * DT)) + 300, 4000).astype(jnp.int32)

    npc = _empty_npcs()
    # slots [0, n_host): forced robots; [n_host, n_host+n_civ): forced civilians (both in the close ring);
    # next n_near slots: random kind at 4..18 m; the rest: random kind at 20..115 m
    keys = jax.random.split(ks[6], N_AMBIENT)
    def body(i, n):
        forced_h = i < n_host
        forced_c = (i >= n_host) & (i < n_host + n_civ)
        forced = forced_h | forced_c
        near = (i >= n_host + n_civ) & (i < n_host + n_civ + n_near)
        rmin = jnp.where(forced, ring_lo, jnp.where(near, 4.0, 20.0))
        rmax = jnp.where(forced, ring_hi, jnp.where(near, 18.0, 115.0))
        fk = jnp.where(forced_h, 1, jnp.where(forced_c, 0, -1))
        return _spawn_slot(world, keys[i], n, i, diff, pos[0], pos[1], rmin, rmax, fk, tries=16)
    npc = jax.lax.fori_loop(0, N_AMBIENT, body, npc)
    # mission sentries: 3 robots 5.5..9 m around the crate (spawnMissionGuards)
    gx, gz = world.goals[g, 0], world.goals[g, 1]
    gkeys = jax.random.split(ks[7], N_GUARD)
    for j in range(N_GUARD):
        i = N_AMBIENT + j
        kk = jax.random.split(gkeys[j], 3)
        okg, x, z = _ring_spot(world, kk[0], gx, gz, 5.5, 9.0, pos[0], pos[1], 0.0, tries=12)
        hp, spd, dmg, cd, aggro, wa = _new_npc_stats(kk[1], diff, 1, True)
        npc = npc._replace(alive=npc.alive.at[i].set(okg), respawn_t=npc.respawn_t.at[i].set(1e9),
                           kind=npc.kind.at[i].set(1), x=npc.x.at[i].set(x), z=npc.z.at[i].set(z),
                           hp=npc.hp.at[i].set(hp), maxhp=npc.maxhp.at[i].set(hp), speed=npc.speed.at[i].set(spd),
                           dmg=npc.dmg.at[i].set(dmg), cd=npc.cd.at[i].set(cd),
                           atk_t=npc.atk_t.at[i].set(0.5 + 0.5 * jax.random.uniform(kk[2])),
                           aggro=npc.aggro.at[i].set(aggro), guard=npc.guard.at[i].set(True),
                           wander_a=npc.wander_a.at[i].set(wa))
    z0 = jnp.float32(0.0)
    phi0 = fighter_phi(world, pos, jnp.float32(100.0), npc) if fighter else -geo0 / 10.0
    st = State(t=jnp.int32(0), max_t=max_t, pos=pos, yaw=yaw, pos0=pos, health=jnp.float32(100.0), armor=jnp.float32(50.0),
               rage=jax.random.uniform(jax.random.fold_in(ks[5], 7), maxval=70.0), berserk_t=z0, atk_cd=z0, score=z0, diff=diff,
               goal=g, goal_xy=jnp.stack([gx, gz]), geo0=geo0, phi=phi0,
               prev_act=jnp.zeros(3, jnp.int32), npc=npc, ep_ret=z0, kills=z0, civ_hits=z0, dmg_taken=z0,
               ktar=jnp.float32(ktar))
    return st


# ----------------------------------------------------------------------------- observation
def observe(world, st: State):
    p, yaw, n = st.pos, st.yaw, st.npc
    patch = patch_obs(world, p, yaw)
    v = []
    v += [st.health / 100.0, st.armor / 50.0, st.rage / 100.0, (st.berserk_t > 0).astype(jnp.float32),
          st.berserk_t / 16.0, st.atk_cd / KICK["cooldown"], in_peace(world, p[0], p[1]).astype(jnp.float32), 1.0]
    s, c, d = range_bearing(p, yaw, st.goal_xy[0], st.goal_xy[1])
    v += [s, c, jnp.log1p(d) / 7.5, jnp.minimum(d, 10.0) / 10.0]
    s, c, d = range_bearing(p, yaw, world.peace[0], world.peace[1])
    v += [s, c, jnp.log1p(d) / 7.5]
    v += list(jax.nn.one_hot(st.diff, 4))
    v += list(jnp.concatenate([jax.nn.one_hot(st.prev_act[0], N_MOVE), jax.nn.one_hot(st.prev_act[1], N_TURN),
                               jax.nn.one_hot(st.prev_act[2], N_ATK)]))
    # nearest NPCs (alive, within 40 m), sorted by distance
    f, r = fwd_right(yaw)
    dx, dz = n.x - p[0], n.z - p[1]
    ahead, right = dx * f[0] + dz * f[1], dx * r[0] + dz * r[1]
    dist = jnp.hypot(dx, dz)
    valid = n.alive & (dist < NPC_RANGE)
    _, idx = jax.lax.top_k(jnp.where(valid, -dist, -1e9), K_OBS)
    looks_civ = (n.kind == 0) | ((n.kind == 2) & ~n.unmasked)
    cos_n = ahead / jnp.maximum(dist, 1e-4)
    facing = cos_n > FACING_COS
    feats = jnp.stack([valid.astype(jnp.float32), ahead / NPC_RANGE, right / NPC_RANGE, dist / NPC_RANGE,
                       looks_civ.astype(jnp.float32), (n.kind == 1).astype(jnp.float32),
                       ((n.kind == 2) & n.unmasked).astype(jnp.float32), n.hp / n.maxhp,
                       (n.stag_t > 0).astype(jnp.float32), (n.prog >= 0).astype(jnp.float32),
                       jnp.minimum(dist, 6.0) / 6.0,
                       (facing & (dist <= JAB["range"])).astype(jnp.float32),
                       (facing & (dist <= KICK["range"])).astype(jnp.float32)], -1)[idx]
    feats = feats * feats[:, :1]                     # zero out empty slots entirely
    vec = jnp.concatenate([jnp.stack([jnp.asarray(x, jnp.float32) for x in v]), feats.reshape(-1)])
    return patch, vec


def privileged(world, st: State):
    """Critic-only / aux targets (never given to the policy)."""
    gd = geo_dist(world, st.goal, st.pos[0], st.pos[1])
    gdir = geo_dir_ego(world, st.goal, st.pos[0], st.pos[1], st.yaw)
    priv = jnp.stack([gd / 1000.0, gdir[0], gdir[1], st.pos[0] / 1000.0, st.pos[1] / 1000.0,
                      (st.max_t - st.t) / 1000.0])
    aux = dict(map=map_target(world, st.pos, st.yaw), geo=jnp.stack([jnp.minimum(gd, 1500.0) / 500.0, gdir[0], gdir[1]]),
               pos=st.pos / 1000.0)
    return priv, aux


# ----------------------------------------------------------------------------- step
def _apply_damage_to_player(health, armor, dmg):
    absorb = jnp.where(armor > 0, jnp.minimum(armor, dmg * 0.65), 0.0)
    return health - (dmg - absorb), armor - absorb


def step(world, st: State, action, key, cur: Curriculum, gamma: float, is_fighter: bool = False):
    ks = jax.random.split(key, 6)
    n = st.npc
    mv, tn, at = action[0], action[1], action[2]
    berserk = st.berserk_t > 0

    # ---- player: turn, then move (2 sub-steps, axis-separated slide like updatePlayer)
    yaw = st.yaw - TURNS[tn]
    f, r = fwd_right(yaw)
    dirs = jnp.stack([jnp.zeros(2), f, -f, -r, r, f])
    d = dirs[mv]
    spd = jnp.where((mv == 5) | berserk, SPRINT, WALK)
    pos = st.pos
    hit_wall = False
    for _ in range(2):
        nx = pos[0] + d[0] * spd * DT / 2
        bx = blocked(world, nx, pos[1])
        pos = pos.at[0].set(jnp.where(bx, pos[0], nx))
        nz = pos[1] + d[1] * spd * DT / 2
        bz = blocked(world, pos[0], nz)
        pos = pos.at[1].set(jnp.where(bz, pos[1], nz))
        hit_wall = hit_wall | (bx | bz)
    hit_wall = hit_wall & (mv != 0)
    px, pz = pos[0], pos[1]
    peace = in_peace(world, px, pz)

    # ---- player attack
    score = st.score
    health, armor, rage, berserk_t = st.health, st.armor, st.rage, st.berserk_t
    can_atk = (at > 0) & (st.atk_cd <= 0)
    dgoal = jnp.hypot(st.goal_xy[0] - px, st.goal_xy[1] - pz)
    mission = can_atk & (dgoal <= 6.5)                         # crate check comes first, even in peace
    swing = can_atk & ~mission & ~peace
    dx, dz = n.x - px, n.z - pz
    hd = jnp.hypot(dx, dz)
    cos_t = (dx * f[0] + dz * f[1]) / jnp.maximum(hd, 1e-4)
    in_cone = cos_t > FACING_COS                               # horizontal facing (game.js checkMeleeHits dotH)
    # glory: nearest staggered fighter within 4 m consumes a primary attack
    stag = n.alive & (n.stag_t > 0) & (n.kind != 0) & (hd < 4.0)
    gi = jnp.argmin(jnp.where(stag, hd, 1e9))
    do_glory = swing & (at == 1) & stag.any()
    jab = swing & (at == 1) & ~do_glory
    kick = swing & (at == 2)
    rng_ = jnp.where(kick, KICK["range"], JAB["range"])
    base = jnp.where(kick, KICK["damage"], JAB["damage"]) * jnp.where(berserk, 3.0, 1.0)
    kb = jnp.where(kick, KICK["kb"], JAB["kb"]) * jnp.where(berserk, 2.2, 1.0)
    hit = (jab | kick) & n.alive & (hd <= rng_) & in_cone
    is_civ = n.kind == 0
    shove = hit & is_civ & berserk                             # berserk never hurts civilians
    hurt = hit & ~shove
    dmg_npc = jnp.where(hurt, base, 0.0)
    glory_hit = do_glory & (jnp.arange(N_NPC) == gi)
    hp = jnp.where(glory_hit, 0.0, n.hp - dmg_npc)
    unmasked = n.unmasked | (hurt & (n.kind == 2))
    # knockback / shove (collision-checked displacement away from the player)
    ux, uz = dx / jnp.maximum(hd, 1e-4), dz / jnp.maximum(hd, 1e-4)
    disp = jnp.where(shove, 0.9, jnp.where(hurt, kb * KB_DISP * jnp.where(is_civ, 0.9, 1.0), 0.0))
    side = jnp.where(jax.random.uniform(ks[0], (N_NPC,)) < 0.5, 1.0, -1.0)
    sx = jnp.where(shove, -uz * side * 0.8 + ux * 0.45, ux); sz = jnp.where(shove, ux * side * 0.8 + uz * 0.45, uz)
    nxk, nzk = n.x + sx * disp, n.z + sz * disp
    okk = ~blocked(world, nxk, nzk)
    x = jnp.where(okk, nxk, n.x); z = jnp.where(okk, nzk, n.z)
    flee_t = jnp.where(hurt & is_civ, 6.0, jnp.where(shove, jnp.maximum(n.flee_t, 2.5), n.flee_t))
    newly_dead = n.alive & (hp <= 0)
    stag_t = jnp.where(hurt & ~is_civ & (hp > 0) & (hp <= 0.32 * n.maxhp), 4.5, n.stag_t)
    # score bookkeeping (killEnemy / hitEnemy)
    civ_hit_n = jnp.sum(hurt & is_civ & ~newly_dead)
    civ_ko_n = jnp.sum(newly_dead & is_civ)
    rob_ko = newly_dead & (n.kind == 1); sna_ko = newly_dead & (n.kind == 2)
    glory_k = glory_hit
    score = score - 100.0 * civ_hit_n - 250.0 * civ_ko_n
    score = score + jnp.sum(rob_ko * jnp.where(glory_k, 500.0, 250.0)) + jnp.sum(sna_ko * jnp.where(glory_k, 600.0, 400.0))
    rage = jnp.minimum(100.0, rage + 25.0 * jnp.sum(rob_ko) + 30.0 * jnp.sum(sna_ko))
    health = jnp.where(do_glory, jnp.minimum(100.0, health + 35.0), health)
    armor = jnp.where(do_glory, jnp.minimum(50.0, armor + 30.0), armor)
    score = score + jnp.where(mission, 1500.0, 0.0)
    health = jnp.where(mission, jnp.minimum(100.0, health + 40.0), health)
    atk_cd = jnp.where(mission, 0.25, jnp.where(do_glory, GLORY_CD, jnp.where(jab, JAB["cooldown"],
                       jnp.where(kick, KICK["cooldown"], st.atk_cd))))
    atk_cd = jnp.maximum(0.0, atk_cd - DT)
    go_berserk = (rage >= 100.0) & (berserk_t <= 0)
    berserk_t = jnp.where(go_berserk, 16.0, berserk_t)
    berserk_t2 = jnp.maximum(0.0, berserk_t - DT)
    rage = jnp.where((berserk_t > 0) & (berserk_t2 <= 0), 0.0, rage)
    berserk_t = berserk_t2
    alive = n.alive & ~newly_dead
    respawn_t = jnp.where(newly_dead, jnp.where(n.guard, 1e9, 4.8), n.respawn_t)   # KO 2.4 s + reinforcement 2.4 s

    # ---- NPC AI (updateEnemies)
    dx, dz = px - x, pz - z
    hd = jnp.hypot(dx, dz)
    ux, uz = dx / jnp.maximum(hd, 1e-4), dz / jnp.maximum(hd, 1e-4)
    fighter = (n.kind == 1) | ((n.kind == 2) & unmasked)
    unmasked = unmasked | ((n.kind == 2) & alive & (hd <= 10.0) & ~peace)
    fighter = (n.kind == 1) | ((n.kind == 2) & unmasked)
    stag_t = jnp.maximum(0.0, stag_t - DT)
    staggered = stag_t > 0
    # civilians & disguised snatchers: wander / flee
    calm = alive & ~fighter
    wt = n.wander_t - DT
    turn_w = wt <= 0
    wa = jnp.where(turn_w, n.wander_a + (jax.random.uniform(ks[1], (N_NPC,)) - 0.5) * jnp.pi * 0.8, n.wander_a)
    wt = jnp.where(turn_w, 3.0 + 4.0 * jax.random.uniform(ks[2], (N_NPC,)), wt)
    fleeing = calm & (flee_t > 0)
    flee_t = jnp.maximum(0.0, flee_t - DT)
    vx = jnp.where(fleeing, -ux * 1.5, jnp.sin(wa) * 0.6) * n.speed
    vz = jnp.where(fleeing, -uz * 1.5, jnp.cos(wa) * 0.6) * n.speed
    # fighters: chase if 1.35 < hd < aggro, player not in sanctuary
    chase = alive & fighter & ~staggered & ~peace & (hd > 1.35) & (hd < n.aggro)
    cnx, cnz = x + ux * n.speed * DT, z + uz * n.speed * DT
    chase = chase & (jnp.hypot(cnx - px, cnz - pz) >= 1.35)
    vx = jnp.where(fighter, jnp.where(chase, ux * n.speed, 0.0), vx)
    vz = jnp.where(fighter, jnp.where(chase, uz * n.speed, 0.0), vz)
    moving = alive & ~(fighter & staggered)
    nx_, nz_ = x + vx * DT, z + vz * DT
    okm = ~blocked(world, nx_, nz_) & moving
    wa = jnp.where(calm & ~fleeing & ~okm, wa + jnp.pi * 0.75, wa)
    wt = jnp.where(calm & ~fleeing & ~okm, 1.0, wt)
    x = jnp.where(okm, nx_, x); z = jnp.where(okm, nz_, z)
    # punches
    dx, dz = px - x, pz - z
    hd = jnp.hypot(dx, dz)
    punching = n.prog >= 0
    can_fight = alive & fighter & ~staggered & ~peace
    atk_t = jnp.where(can_fight & ~punching & (hd <= 2.2), n.atk_t - DT, n.atk_t)
    start = can_fight & ~punching & (atk_t <= 0) & (hd <= 2.2)
    atk_t = jnp.where(start, n.cd + 0.4 * jax.random.uniform(ks[3], (N_NPC,)), atk_t)
    prog = jnp.where(start, 0.0, n.prog)
    prog2 = jnp.where(prog >= 0, prog + DT * 3.2, prog)
    lands = can_fight & (prog >= 0) & (prog < 0.5) & (prog2 >= 0.5) & (hd <= 2.4)
    prog = jnp.where(prog2 >= 1.0, -1.0, prog2)
    prog = jnp.where(alive & fighter & ~staggered, prog, -1.0)
    dmg_in = jnp.sum(jnp.where(lands, n.dmg, 0.0))
    h0, a0 = health, armor
    health, armor = _apply_damage_to_player(health, armor, dmg_in)
    # sanctuary regeneration
    health = jnp.where(peace, jnp.minimum(100.0, health + 8.0 * DT), health)
    armor = jnp.where(peace, jnp.minimum(50.0, armor + 5.0 * DT), armor)

    npc = n._replace(alive=alive, respawn_t=respawn_t, unmasked=unmasked, x=x, z=z, hp=hp, atk_t=atk_t, prog=prog,
                     stag_t=stag_t, flee_t=flee_t, wander_a=wa, wander_t=wt)

    # ---- roaming: cull > 115 m, respawn dead/culled ambient slots 32..77 m away (one per step)
    far = npc.alive & ~npc.guard & (jnp.hypot(npc.x - px, npc.z - pz) > 115.0)
    respawn_t = jnp.where(far, 0.0, npc.respawn_t)
    alive = npc.alive & ~far
    respawn_t = jnp.where(~alive & ~npc.guard, respawn_t - DT, respawn_t)
    npc = npc._replace(alive=alive, respawn_t=respawn_t)
    due = (~npc.alive) & (~npc.guard) & (npc.respawn_t <= 0)
    slot = jnp.argmax(due)
    npc = jax.lax.cond(due.any(), lambda q: _spawn_slot(world, ks[4], q, slot, st.diff, px, pz, 32.0, 77.0),
                       lambda q: q, npc)

    # ---- reward
    t = st.t + 1
    dead = health <= 0
    bad_kos = jnp.sum(rob_ko | sna_ko)
    bad_hits = jnp.sum(hurt & ((n.kind == 1) | (n.kind == 2)))
    wall_pen = jnp.where(hit_wall, 0.05, 0.0)                  # global: grinding into buildings costs a little
    if not is_fighter:
        # CRATE RUNNER. Progress shaping: F = Phi(s') - Phi(s), Phi = -geodesic/10. Summed over an episode this
        # is exactly 0.1 x (geodesic progress), whatever gamma is and however the episode ends. (The
        # gamma*Phi(s') - Phi(s) form with a negative Phi pays (1-gamma)|Phi| per step for merely being far
        # away, which an earlier run exploited on >1 km routes once the mission bonus was discounted to nothing.)
        gd = geo_dist(world, st.goal, px, pz)
        phi = -gd / 10.0
        success = mission
        timeout = (t >= st.max_t) & ~success & ~dead
        heal_r = jnp.where(peace & (health < 85.0), 0.25, 0.0)
        game_r = (score - st.score) / 250.0 - 0.02 * jnp.maximum(0.0, h0 - health) \
            - 0.01 * jnp.maximum(0.0, a0 - armor) - 5.0 * dead - 2.0 * timeout + 50.0 * success \
            + heal_r + 4.0 * bad_kos - 10.0 * civ_hit_n - 25.0 * civ_ko_n - wall_pen
    else:
        # STREET BRAWLER. No crate objective at all. Win = reach this episode's KO target (curriculum stage).
        phi = fighter_phi(world, pos, health, npc)
        success = (st.kills + bad_kos) >= st.ktar
        timeout = (t >= st.max_t) & ~success & ~dead
        heal_r = jnp.where(peace & (health < 80.0), 0.3, 0.0)
        game_r = 20.0 * bad_kos + 10.0 * jnp.sum(glory_k) + 3.0 * bad_hits \
            - 25.0 * civ_hit_n - 50.0 * civ_ko_n - 15.0 * dead - 0.03 * jnp.maximum(0.0, h0 - health) \
            + heal_r + 10.0 * success - wall_pen
    shaping = phi - st.phi
    reward = game_r + shaping
    done = success | dead | timeout

    nst = st._replace(t=t, pos=pos, yaw=yaw, pos0=st.pos0, health=health, armor=armor, rage=rage, berserk_t=berserk_t,
                      atk_cd=atk_cd, score=score, phi=phi, prev_act=action.astype(jnp.int32), npc=npc,
                      ep_ret=st.ep_ret + game_r, kills=st.kills + bad_kos,
                      civ_hits=st.civ_hits + civ_hit_n + civ_ko_n, dmg_taken=st.dmg_taken + dmg_in)
    info = dict(done=done, success=success, dead=dead, timeout=timeout, geo0=st.geo0, ep_ret=nst.ep_ret, score=score,
                ep_len=t, kills=nst.kills, civ_hits=nst.civ_hits, dmg_taken=nst.dmg_taken, diff=st.diff,
                start_x=st.pos0[0], start_z=st.pos0[1], ktar=st.ktar)
    # (no auto-reset here: the trainer swaps in a pre-generated spare start state on `done`,
    #  which is ~4x cheaper than computing a full reset for every env on every step under vmap)
    return nst, reward, done, info


def expert_act(world, st: State):
    """
    Teacher / oracle action: combines shortest-path geodesic navigation with reactive combat.
    Reaches crates with >99% success rate across Toronto street networks.
    """
    p, yaw = st.pos, st.yaw
    gdir = geo_dir_ego(world, st.goal, p[0], p[1], yaw)
    ahead, right = gdir[0], gdir[1]
    ang = jnp.arctan2(right, ahead)
    
    # 5 discrete turns in TURNS [-0.5, -0.15, 0.0, 0.15, 0.5]
    tn = jnp.argmin(jnp.abs(TURNS - ang))
    
    # 6 discrete moves: 0:none, 1:fwd, 2:back, 3:left, 4:right, 5:sprint
    mv = jnp.where(ahead > 0.35, 5, jnp.where(ahead > -0.2, 1, 0))
    
    # combat: hit mission crate when close, or attack nearest enemy in cone
    dgoal = jnp.hypot(st.goal_xy[0] - p[0], st.goal_xy[1] - p[1])
    at_crate = dgoal <= 6.5
    
    dx, dz = st.npc.x - p[0], st.npc.z - p[1]
    dist = jnp.hypot(dx, dz)
    f, r = fwd_right(yaw)
    n_ahead = dx * f[0] + dz * f[1]
    in_cone = n_ahead / jnp.maximum(dist, 1e-4) > 0.55
    is_fighter = (st.npc.kind == 1) | (st.npc.kind == 2)
    near_enemy = st.npc.alive & is_fighter & in_cone & (dist < 3.5)
    
    at = jnp.where(at_crate, 2, jnp.where(near_enemy.any(), 1, 0))
    return jnp.stack([mv, tn, at])


def expert_act_fighter(world, st: State):
    """
    Teacher / oracle action for BRAWLER / ENFORCER mode:
    Actively hunts hostile robots and revealed snatchers, executes glory kills on staggered foes,
    lands heavy kicks and light jabs, circles enemies, strictly avoids hitting civilians,
    and retreats to the CN Tower / Pecaut Square peace sanctuary when critically wounded.
    """
    p, yaw = st.pos, st.yaw
    f, r = fwd_right(yaw)
    low_hp = st.health < 40.0
    s_dx = world.peace[0] - p[0]
    s_dz = world.peace[1] - p[1]
    s_ahead = s_dx * f[0] + s_dz * f[1]
    s_right = s_dx * r[0] + s_dz * r[1]
    s_ang = jnp.arctan2(s_right, s_ahead)
    s_tn = jnp.argmin(jnp.abs(TURNS - s_ang))
    s_mv = jnp.where(s_ahead > 0.3, 5, 1)

    is_bad = st.npc.alive & ((st.npc.kind == 1) | ((st.npc.kind == 2) & st.npc.unmasked))
    dx = st.npc.x - p[0]
    dz = st.npc.z - p[1]
    dist = jnp.hypot(dx, dz)
    bad_dist = jnp.where(is_bad, dist, 1e9)
    closest_idx = jnp.argmin(bad_dist)
    has_hostile = bad_dist[closest_idx] < 50.0

    t_dx = st.npc.x[closest_idx] - p[0]
    t_dz = st.npc.z[closest_idx] - p[1]
    t_dist = bad_dist[closest_idx]
    t_ahead = t_dx * f[0] + t_dz * f[1]
    t_right = t_dx * r[0] + t_dz * r[1]
    t_ang = jnp.arctan2(t_right, t_ahead)
    t_tn = jnp.argmin(jnp.abs(TURNS - t_ang))

    in_reach = t_dist < 3.8
    is_staggered = st.npc.stag_t[closest_idx] > 0
    atk_choice = jnp.where(is_staggered, 1, jnp.where(t_dist > 2.6, 2, 1))
    f_at = jnp.where(in_reach & (t_ahead > 0.4), atk_choice, 0)
    f_mv = jnp.where(in_reach, jnp.where(t_ahead > 1.2, 1, 0), jnp.where(t_ahead > 0.3, 5, 1))

    g_act = expert_act(world, st)
    mv = jnp.where(low_hp, s_mv, jnp.where(has_hostile, f_mv, g_act[0]))
    tn = jnp.where(low_hp, s_tn, jnp.where(has_hostile, t_tn, g_act[1]))
    at = jnp.where(low_hp, 0, jnp.where(has_hostile, f_at, g_act[2]))
    return jnp.stack([mv, tn, at])

