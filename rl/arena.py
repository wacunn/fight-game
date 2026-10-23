"""
1v1 Pure Boxing Arena environment in JAX.

Simulates a bounded 14m x 14m ring with 1 player and 1 hostile combatant.
Isolates combat mechanics completely so PPO gradients focus 100% on:
  - Spacing and footwork (closing distance without sprint overshoot)
  - Punch and kick timing (jabs, heavy kicks, counter-strikes)
  - Glory kills on staggered foes
  - Dodging enemy windup punches
  - Zero civilian / crate distraction

Observations (16x16 patch, 111-dim vector) and actions ([6, 5, 3]) are 100%
compatible with rl/env.py and ai_copilot.js (obs_version 2).
"""
from typing import NamedTuple
import jax
import jax.numpy as jnp
import numpy as np

import env as E

RING_HALF = 6.0                 # 12m x 12m walkable interior, boundary walls at +-6m
ARENA_MAX_T = 250               # 25 seconds of non-stop action per bout
TURNS = E.TURNS                 # [-0.5, -0.15, 0.0, 0.15, 0.5]
DT = E.DT                       # 0.1 s
WALK, SPRINT = E.WALK, E.SPRINT # 7.0, 11.5 m/s

JAB = E.JAB                     # dmg 30, range 3.5, cd 0.22, kb 6.0
KICK = E.KICK                   # dmg 100, range 4.2, cd 0.55, kb 32.0


class ArenaState(NamedTuple):
    t: jnp.ndarray              # int step counter
    pos: jnp.ndarray            # (2,) player (x, z)
    yaw: jnp.ndarray            # float player yaw
    health: jnp.ndarray         # float player health (0..100)
    armor: jnp.ndarray          # float player armor (0..50)
    rage: jnp.ndarray           # float player rage (0..100)
    berserk_t: jnp.ndarray      # float berserk duration remaining
    atk_cd: jnp.ndarray         # float player attack cooldown
    prev_act: jnp.ndarray       # (3,) int [mv, tn, at]
    
    # 1v1 Enemy state
    enemy_pos: jnp.ndarray      # (2,) enemy (x, z)
    enemy_hp: jnp.ndarray       # float enemy health (0..100)
    enemy_maxhp: jnp.ndarray    # float 100.0
    enemy_speed: jnp.ndarray    # float 3.6 m/s
    enemy_dmg: jnp.ndarray      # float 16.0
    enemy_prog: jnp.ndarray     # float punch anim (-1.0 = idle, 0..1 = punching)
    enemy_stag_t: jnp.ndarray   # float stagger duration (>0 = vulnerable to glory kill)
    enemy_atk_t: jnp.ndarray    # float enemy attack cooldown
    
    # Bout stats
    ep_ret: jnp.ndarray
    won: jnp.ndarray
    dead: jnp.ndarray


def fwd_right(yaw):
    s, c = jnp.sin(yaw), jnp.cos(yaw)
    return jnp.stack([-s, -c], -1), jnp.stack([c, -s], -1)


def reset(key):
    k_pos, k_e, k_rot = jax.random.split(key, 3)
    # Player spawns at western side (-3.5, uniform z in [-2, 2]), facing east (yaw = -pi/2)
    pz = jax.random.uniform(k_pos, (), minval=-2.0, maxval=2.0)
    px = -3.5 + jax.random.uniform(k_pos, (), minval=-0.5, maxval=0.5)
    pyaw = -jnp.pi / 2.0 + (jax.random.uniform(k_rot, ()) - 0.5) * 0.3
    
    # Enemy spawns at eastern side (+3.5, uniform z in [-2, 2])
    ez = jax.random.uniform(k_e, (), minval=-2.0, maxval=2.0)
    ex = 3.5 + jax.random.uniform(k_e, (), minval=-0.5, maxval=0.5)
    
    return ArenaState(
        t=jnp.int32(0), pos=jnp.stack([px, pz]), yaw=pyaw,
        health=jnp.float32(100.0), armor=jnp.float32(25.0), rage=jnp.float32(0.0),
        berserk_t=jnp.float32(0.0), atk_cd=jnp.float32(0.0),
        prev_act=jnp.zeros(3, jnp.int32),
        enemy_pos=jnp.stack([ex, ez]), enemy_hp=jnp.float32(100.0),
        enemy_maxhp=jnp.float32(100.0), enemy_speed=jnp.float32(3.6),
        enemy_dmg=jnp.float32(15.0), enemy_prog=jnp.float32(-1.0),
        enemy_stag_t=jnp.float32(0.0), enemy_atk_t=jnp.float32(0.6),
        ep_ret=jnp.float32(0.0), won=jnp.bool_(False), dead=jnp.bool_(False)
    )


def observe(st: ArenaState):
    """Produces 16x16 patch and 111-dim vector identical to E.observe()."""
    f, r = fwd_right(st.yaw)
    p = st.pos
    
    # 1. 16x16 egocentric patch (2m cells): 1.0 if outside ring boundary [-6, 6]
    ii = jnp.arange(E.PATCH, dtype=jnp.float32)
    ahead = (E.PATCH_ROW0 - ii) * E.PATCH_CELL
    right = (ii - (E.PATCH - 1) / 2.0) * E.PATCH_CELL
    A, R = jnp.meshgrid(ahead, right, indexing="ij")
    X = p[0] + A * f[0] + R * r[0]
    Z = p[1] + A * f[1] + R * r[1]
    patch = ((jnp.abs(X) >= RING_HALF) | (jnp.abs(Z) >= RING_HALF)).astype(jnp.float32)
    
    # 2. 111-dim vector
    v = [
        st.health / 100.0, st.armor / 50.0, st.rage / 100.0, (st.berserk_t > 0).astype(jnp.float32),
        st.berserk_t / 16.0, st.atk_cd / KICK["cooldown"], 0.0, 1.0   # 0..7
    ]
    # Goal: enemy position serves as the primary guidance beacon
    dx_g, dz_g = st.enemy_pos[0] - p[0], st.enemy_pos[1] - p[1]
    g_a, g_r = dx_g * f[0] + dz_g * f[1], dx_g * r[0] + dz_g * r[1]
    g_d = jnp.hypot(g_a, g_r)
    g_ang = jnp.arctan2(g_r, g_a)
    v += [jnp.sin(g_ang), jnp.cos(g_ang), jnp.log1p(g_d) / 7.5, jnp.minimum(g_d, 10.0) / 10.0] # 8..11
    v += [0.0, 0.0, 0.0]                                          # 12..14 (peace sanctuary - none in arena)
    v += [0.0, 1.0, 0.0, 0.0]                                     # 15..18 (medium difficulty one-hot)
    v += list(jnp.concatenate([
        jax.nn.one_hot(st.prev_act[0], E.N_MOVE),
        jax.nn.one_hot(st.prev_act[1], E.N_TURN),
        jax.nn.one_hot(st.prev_act[2], E.N_ATK)
    ]))                                                            # 19..32 (previous action one-hot)
    
    # NPC slot 0: The 1v1 Enemy Robot
    e_alive = st.enemy_hp > 0
    dx_e, dz_e = st.enemy_pos[0] - p[0], st.enemy_pos[1] - p[1]
    e_ahead, e_right = dx_e * f[0] + dz_e * f[1], dx_e * r[0] + dz_e * r[1]
    e_dist = jnp.hypot(dx_e, dz_e)
    cos_n = e_ahead / jnp.maximum(e_dist, 1e-4)
    facing = cos_n > E.FACING_COS
    
    slot0 = jnp.array([
        e_alive.astype(jnp.float32),
        e_ahead / E.NPC_RANGE, e_right / E.NPC_RANGE, e_dist / E.NPC_RANGE,
        0.0,                                                      # looks_civ = 0
        1.0,                                                      # robot = 1
        0.0,                                                      # snatcher = 0
        st.enemy_hp / st.enemy_maxhp,
        (st.enemy_stag_t > 0).astype(jnp.float32),
        (st.enemy_prog >= 0).astype(jnp.float32),
        jnp.minimum(e_dist, 6.0) / 6.0,
        (facing & (e_dist <= JAB["range"])).astype(jnp.float32),
        (facing & (e_dist <= KICK["range"])).astype(jnp.float32)
    ], dtype=jnp.float32) * e_alive.astype(jnp.float32)
    
    # Empty slots 1..5 (5 * 13 = 65 zeros)
    empty_slots = jnp.zeros(5 * E.NPC_FEATS, dtype=jnp.float32)
    vec = jnp.concatenate([jnp.stack([jnp.asarray(x, jnp.float32) for x in v]), slot0, empty_slots])
    return patch, vec


def privileged(st: ArenaState):
    """Critic inputs (arena version)."""
    dx, dz = st.enemy_pos[0] - st.pos[0], st.enemy_pos[1] - st.pos[1]
    dist = jnp.hypot(dx, dz)
    f, r = fwd_right(st.yaw)
    ahead, right = dx * f[0] + dz * f[1], dx * r[0] + dz * r[1]
    priv = jnp.stack([dist / 20.0, ahead / 20.0, right / 20.0, st.pos[0] / 10.0, st.pos[1] / 10.0,
                      (ARENA_MAX_T - st.t) / ARENA_MAX_T])
    aux = dict(
        map=jnp.zeros((E.MAP * E.MAP,), jnp.float32),
        geo=jnp.stack([dist / 10.0, ahead / jnp.maximum(dist, 1e-4), right / jnp.maximum(dist, 1e-4)]),
        pos=st.pos / 10.0
    )
    return priv, aux


def step(st: ArenaState, action, key):
    ks = jax.random.split(key, 4)
    mv, tn, at = action[0], action[1], action[2]
    berserk = st.berserk_t > 0
    
    # 1. Player turn & move
    yaw = st.yaw - TURNS[tn]
    f, r = fwd_right(yaw)
    dirs = jnp.stack([jnp.zeros(2), f, -f, -r, r, f])
    d = dirs[mv]
    spd = jnp.where((mv == 5) | berserk, SPRINT, WALK)
    npos = st.pos + d * spd * DT
    # Clamped collision against arena ring boundary
    px = jnp.clip(npos[0], -RING_HALF + 0.3, RING_HALF - 0.3)
    pz = jnp.clip(npos[1], -RING_HALF + 0.3, RING_HALF - 0.3)
    pos = jnp.stack([px, pz])
    
    # 2. Player attack resolution
    can_atk = (at > 0) & (st.atk_cd <= 0)
    dx, dz = st.enemy_pos[0] - px, st.enemy_pos[1] - pz
    hd = jnp.hypot(dx, dz)
    cos_t = (dx * f[0] + dz * f[1]) / jnp.maximum(hd, 1e-4)
    in_cone = cos_t > E.FACING_COS
    
    e_alive = st.enemy_hp > 0
    e_staggered = e_alive & (st.enemy_stag_t > 0)
    
    do_glory = can_atk & (at == 1) & e_staggered & (hd < 4.0)
    jab = can_atk & (at == 1) & ~do_glory
    kick = can_atk & (at == 2)
    
    rng_ = jnp.where(kick, KICK["range"], JAB["range"])
    base_dmg = jnp.where(kick, KICK["damage"], JAB["damage"]) * jnp.where(berserk, 3.0, 1.0)
    kb = jnp.where(kick, KICK["kb"], JAB["kb"]) * jnp.where(berserk, 2.2, 1.0)
    
    hit = (jab | kick) & e_alive & (hd <= rng_) & in_cone
    dmg = jnp.where(hit, base_dmg, 0.0)
    
    new_e_hp = jnp.where(do_glory, 0.0, jnp.maximum(0.0, st.enemy_hp - dmg))
    e_newly_dead = e_alive & (new_e_hp <= 0)
    
    # Enemy stagger: if knocked down below 32% hp and not dead
    new_stag_t = jnp.where(hit & (new_e_hp > 0) & (new_e_hp <= 32.0), 4.5, jnp.maximum(0.0, st.enemy_stag_t - DT))
    
    # Knockback displacement
    ux, uz = dx / jnp.maximum(hd, 1e-4), dz / jnp.maximum(hd, 1e-4)
    disp = jnp.where(hit, kb * E.KB_DISP, 0.0)
    ex = jnp.clip(st.enemy_pos[0] + ux * disp, -RING_HALF + 0.3, RING_HALF - 0.3)
    ez = jnp.clip(st.enemy_pos[1] + uz * disp, -RING_HALF + 0.3, RING_HALF - 0.3)
    
    # Player cooldown & rage
    atk_cd = jnp.where(do_glory, E.GLORY_CD, jnp.where(jab, JAB["cooldown"], jnp.where(kick, KICK["cooldown"], st.atk_cd)))
    atk_cd = jnp.maximum(0.0, atk_cd - DT)
    raw_rage = jnp.minimum(100.0, st.rage + jnp.where(hit, 15.0, 0.0) + jnp.where(e_newly_dead, 35.0, 0.0))
    trigger_berserk = (raw_rage >= 100.0) & (st.berserk_t <= 0)
    berserk_t = jnp.where(trigger_berserk, 16.0, jnp.maximum(0.0, st.berserk_t - DT))
    rage = jnp.where(trigger_berserk, 0.0, raw_rage)
    
    # 3. Enemy AI (chase & punch)
    edx, edz = px - ex, pz - ez
    ehd = jnp.hypot(edx, edz)
    eux, euz = edx / jnp.maximum(ehd, 1e-4), edz / jnp.maximum(ehd, 1e-4)
    
    can_enemy_fight = (new_e_hp > 0) & (new_stag_t <= 0)
    chase = can_enemy_fight & (ehd > 1.35)
    ex = jnp.where(chase, jnp.clip(ex + eux * st.enemy_speed * DT, -RING_HALF + 0.3, RING_HALF - 0.3), ex)
    ez = jnp.where(chase, jnp.clip(ez + euz * st.enemy_speed * DT, -RING_HALF + 0.3, RING_HALF - 0.3), ez)
    enemy_pos = jnp.stack([ex, ez])
    
    # Enemy punch windup & strike
    ehd2 = jnp.hypot(px - ex, pz - ez)
    e_punching = st.enemy_prog >= 0
    e_atk_t = jnp.where(can_enemy_fight & ~e_punching & (ehd2 <= 2.2), st.enemy_atk_t - DT, st.enemy_atk_t)
    e_start_punch = can_enemy_fight & ~e_punching & (e_atk_t <= 0) & (ehd2 <= 2.2)
    e_atk_t = jnp.where(e_start_punch, 1.0 + 0.3 * jax.random.uniform(ks[0]), e_atk_t)
    
    prog = jnp.where(e_start_punch, 0.0, st.enemy_prog)
    prog2 = jnp.where(prog >= 0, prog + DT * 3.2, prog)
    enemy_punch_lands = can_enemy_fight & (prog >= 0) & (prog < 0.5) & (prog2 >= 0.5) & (ehd2 <= 2.4)
    prog = jnp.where(prog2 >= 1.0, -1.0, prog2)
    prog = jnp.where(can_enemy_fight, prog, -1.0)
    
    dmg_to_player = jnp.where(enemy_punch_lands, st.enemy_dmg, 0.0)
    absorb = jnp.where(st.armor > 0, jnp.minimum(st.armor, dmg_to_player * 0.65), 0.0)
    health = jnp.maximum(0.0, st.health - (dmg_to_player - absorb))
    armor = jnp.maximum(0.0, st.armor - absorb)
    
    # Glory kill bonus: heals player
    health = jnp.where(do_glory, jnp.minimum(100.0, health + 35.0), health)
    armor = jnp.where(do_glory, jnp.minimum(50.0, armor + 30.0), armor)
    
    dead = health <= 0
    won = new_e_hp <= 0
    t = st.t + 1
    timeout = (t >= ARENA_MAX_T) & ~won & ~dead
    done = won | dead | timeout
    
    # 4. Dense combat reward function
    # Strike rewards
    r_jab = jnp.where(hit & jab, 3.5, 0.0)
    r_kick = jnp.where(hit & kick, 8.0, 0.0)
    r_glory = jnp.where(do_glory, 18.0, 0.0)
    r_ko = jnp.where(e_newly_dead, 45.0, 0.0)
    
    # Defense & damage penalties
    r_dmg_taken = -0.05 * dmg_to_player
    r_death = jnp.where(dead, -20.0, 0.0)
    
    # Spacing shaping: reward closing distance when far, reward squaring up in melee
    prev_hd = jnp.hypot(st.enemy_pos[0] - st.pos[0], st.enemy_pos[1] - st.pos[1])
    r_approach = jnp.where(hd > 2.8, (prev_hd - hd) * 0.8, 0.0)
    r_facing = jnp.where((hd <= 3.5) & in_cone, 0.15, 0.0)
    
    # Footwork: penalize sprinting inside melee range (overshooting)
    r_sprint_pen = jnp.where((mv == 5) & (hd < 2.5), -0.15, 0.0)
    # Whiff penalty: swinging when completely out of reach
    r_whiff = jnp.where(can_atk & ~hit & ~do_glory & (hd > 4.5), -0.1, 0.0)
    
    reward = r_jab + r_kick + r_glory + r_ko + r_dmg_taken + r_death + r_approach + r_facing + r_sprint_pen + r_whiff
    
    nst = st._replace(
        t=t, pos=pos, yaw=yaw, health=health, armor=armor, rage=rage, berserk_t=berserk_t,
        atk_cd=atk_cd, prev_act=action.astype(jnp.int32),
        enemy_pos=enemy_pos, enemy_hp=new_e_hp, enemy_prog=prog, enemy_stag_t=new_stag_t,
        enemy_atk_t=e_atk_t, ep_ret=st.ep_ret + reward, won=won, dead=dead
    )
    info = dict(
        done=done, success=won, dead=dead, timeout=timeout,
        ep_ret=nst.ep_ret, ep_len=t, kills=won.astype(jnp.float32),
        dmg_taken=dmg_to_player, hits_landed=hit.astype(jnp.float32)
    )
    return nst, reward, done, info


def expert_act(st: ArenaState):
    """
    Expert heuristic teacher for the arena:
    - Maintains combat spacing (walks/circles, avoids blind sprinting inside 3.5m)
    - Turns to face the enemy directly
    - Throws jabs and kicks when within range and facing
    - Triggers glory kill on staggered enemy
    - Slips/circles when enemy is winding up a punch
    """
    p, yaw = st.pos, st.yaw
    f, r = fwd_right(yaw)
    dx, dz = st.enemy_pos[0] - p[0], st.enemy_pos[1] - p[1]
    dist = jnp.hypot(dx, dz)
    ahead, right = dx * f[0] + dz * f[1], dx * r[0] + dz * r[1]
    ang = jnp.arctan2(right, ahead)
    
    # Align yaw to face the opponent directly
    tn = jnp.argmin(jnp.abs(TURNS - ang))
    
    # Footwork:
    # If far (> 3.8m): sprint or walk forward
    # If in striking pocket (2.2m - 3.5m): walk forward
    # If inside pocket (< 2.2m):
    #   if enemy punching: step back (mv = 2) or strafe (mv = 3)
    #   else: step in or hold
    e_punching = st.enemy_prog >= 0
    mv = jnp.where(
        dist > 3.8,
        jnp.where(ahead > 0.4, 5, 1), # sprint approach
        jnp.where(
            dist > 2.4,
            1,                          # walk in
            jnp.where(e_punching, 2, 0) # slip back on incoming punch, else hold/plant
        )
    )
    
    # Attacks:
    is_staggered = st.enemy_stag_t > 0
    in_jab = (dist <= JAB["range"]) & (ahead > 0.3)
    in_kick = (dist <= KICK["range"]) & (ahead > 0.3)
    
    at = jnp.where(
        is_staggered & (dist < 4.0),
        1,                             # glory kill
        jnp.where(
            in_kick & (dist > 2.8),
            2,                         # heavy kick at outer range
            jnp.where(in_jab, 1, 0)    # jab in pocket
        )
    )
    return jnp.stack([mv, tn, at])
