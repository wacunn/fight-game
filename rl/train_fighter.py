#!/usr/bin/env python3
"""
PPO-LSTM training for the BRAWLER / ENFORCER AI model ("Fight Mode").
Initializes from the 50M Crate Runner checkpoint, and optimizes for:
  - Aggressively hunting and defeating bad guys (robots and unmasked snatchers)
  - Landing combo jabs, heavy kicks, and glory kills on staggered foes
  - Strict zero-tolerance penalty for harming civilians
  - Tactical retreats to the CN Tower / Pecaut Square peace sanctuary when wounded
  - Exports to ai_model_fighter.json
"""
import argparse
import functools
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax
import jax.numpy as jnp
import numpy as np
import optax

import agent as A
import districts
import env as E
import world as W

ROOT = os.path.abspath(os.path.join(HERE, ".."))


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--envs", type=int, default=128)
    ap.add_argument("--rollout", type=int, default=64)
    ap.add_argument("--steps", type=int, default=10_000_000)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--hidden", type=int, default=128)
    ap.add_argument("--channels", default="8,16,16")
    ap.add_argument("--minibatches", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--gamma", type=float, default=0.998)
    ap.add_argument("--lam", type=float, default=0.95)
    ap.add_argument("--clip", type=float, default=0.2)
    ap.add_argument("--ent", type=float, default=0.015)
    ap.add_argument("--vf", type=float, default=0.5)
    ap.add_argument("--w-fut", type=float, default=0.5)
    ap.add_argument("--w-map", type=float, default=0.5)
    ap.add_argument("--w-geo", type=float, default=0.25)
    ap.add_argument("--w-probe", type=float, default=1.0)
    ap.add_argument("--w-bc", type=float, default=1.2, help="teacher behavioral cloning / imitation loss weight")
    ap.add_argument("--teacher-eps", type=float, default=0.5, help="initial fraction of teacher-guided envs")
    ap.add_argument("--teacher-decay", type=float, default=0.9992, help="teacher guidance decay per update")
    ap.add_argument("--cur-start", type=float, default=40.0)
    ap.add_argument("--cur-max", type=float, default=1200.0)
    ap.add_argument("--export-every", type=int, default=25, help="updates between ai_model_fighter.json exports")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--resume", action="store_true", help="resume training from fighter_latest.pkl")
    ap.add_argument("--init-ckpt", default=os.path.join(HERE, "checkpoints", "runner_50m.pkl"))
    return ap.parse_args()


def build_fns(world, cfg):
    N, T = cfg.envs, cfg.rollout
    vreset = jax.vmap(lambda k, cur: E.reset(world, k, cur, fighter=True), in_axes=(0, None))
    # Step with is_fighter=True
    vstep = jax.vmap(lambda s, a, k, cur: E.step(world, s, a, k, cur, cfg.gamma, is_fighter=True), in_axes=(0, 0, 0, None))
    vobs = jax.vmap(lambda s: E.observe(world, s))
    vpriv = jax.vmap(lambda s: E.privileged(world, s))
    vexpert = jax.vmap(lambda s: E.expert_act_fighter(world, s))

    def first_carry(key, cur):
        k1, k2, k3 = jax.random.split(key, 3)
        st = vreset(jax.random.split(k1, N), cur)
        spare = vreset(jax.random.split(k2, N), cur)
        patch, vec = vobs(st); priv, aux = vpriv(st)
        z = jnp.zeros((N, A.H))
        return dict(st=st, hc=(z, z), patch=patch, vec=vec, priv=priv, aux=aux,
                    resetf=jnp.ones(N, bool), spare=spare, key=k3)

    @jax.jit
    def rollout(params, carry, cur, teacher_eps):
        def step_fn(c, t):
            key, k_act, k_env, k_sp, k_teach = jax.random.split(c["key"], 5)
            spare = jax.lax.cond(t % 32 == 0, lambda _: vreset(jax.random.split(k_sp, N), cur), lambda _: c["spare"], None)
            m = c["resetf"][:, None]
            hc = (jnp.where(m, 0.0, c["hc"][0]), jnp.where(m, 0.0, c["hc"][1]))
            h, hc = A.lstm(params, A.encode(params, c["patch"], c["vec"]), hc)
            logits, v = A.heads(params, h, c["priv"])
            acts, logp = A.sample(k_act, logits)

            exp_acts = vexpert(c["st"])
            teach_mask = jax.random.uniform(k_teach, (N,)) < teacher_eps
            exec_acts = jnp.where(teach_mask[:, None], exp_acts, acts)
            exec_logp = jnp.where(teach_mask, A.log_prob(logits, exp_acts), logp)

            nst, r, done, info = vstep(c["st"], exec_acts, jax.random.split(k_env, N), cur)
            tp, tv = vobs(nst); tpriv, _ = vpriv(nst)
            th, _ = A.lstm(params, A.encode(params, tp, tv), hc)
            _, v_term = A.heads(params, th, tpriv)
            r = r + cfg.gamma * jnp.where(info["timeout"], jax.lax.stop_gradient(v_term), 0.0)
            nst = jax.tree_util.tree_map(lambda a, b: jnp.where(done.reshape((-1,) + (1,) * (a.ndim - 1)), a, b), spare, nst)
            patch, vec = vobs(nst); priv, aux = vpriv(nst)
            tr = dict(patch=c["patch"].astype(jnp.uint8), vec=c["vec"], priv=c["priv"], aux=c["aux"], resetf=c["resetf"],
                      acts=exec_acts, exp_acts=exp_acts, logp=exec_logp, v=v, r=r, done=done, info=info)
            nc = dict(st=nst, hc=hc, patch=patch, vec=vec, priv=priv, aux=aux, resetf=done, spare=spare, key=key)
            return nc, tr

        hc0 = carry["hc"]; resetf0 = carry["resetf"]
        carry, traj = jax.lax.scan(step_fn, carry, jnp.arange(T))
        m = carry["resetf"][:, None]
        hc = (jnp.where(m, 0.0, carry["hc"][0]), jnp.where(m, 0.0, carry["hc"][1]))
        h, _ = A.lstm(params, A.encode(params, carry["patch"], carry["vec"]), hc)
        _, last_v = A.heads(params, h, carry["priv"])
        return carry, traj, last_v, hc0, resetf0

    def gae(r, v, done, last_v):
        def f(c, x):
            adv, nv = c
            r_, v_, d_ = x
            delta = r_ + cfg.gamma * nv * (1 - d_) - v_
            adv = delta + cfg.gamma * cfg.lam * (1 - d_) * adv
            return (adv, v_), adv
        _, adv = jax.lax.scan(f, (jnp.zeros_like(last_v), last_v), (r, v, done.astype(jnp.float32)), reverse=True)
        return adv, adv + v

    def loss_fn(params, mb):
        def f(hc, x):
            patch, vec, rf = x
            m = rf[:, None]
            hc = (jnp.where(m, 0.0, hc[0]), jnp.where(m, 0.0, hc[1]))
            h, hc = A.lstm(params, A.encode(params, patch, vec), hc)
            return hc, h
        _, hs = jax.lax.scan(f, mb["hc0"], (mb["patch"].astype(jnp.float32), mb["vec"], mb["resetf"]))
        logits, v = A.heads(params, hs, mb["priv"])
        logp = A.log_prob(logits, mb["acts"])
        ratio = jnp.exp(logp - mb["logp"])
        adv = (mb["adv"] - mb["adv"].mean()) / (mb["adv"].std() + 1e-8)
        pg = -jnp.mean(jnp.minimum(ratio * adv, jnp.clip(ratio, 1 - cfg.clip, 1 + cfg.clip) * adv))
        v_cl = mb["v"] + jnp.clip(v - mb["v"], -cfg.clip, cfg.clip)
        vf = 0.5 * jnp.mean(jnp.maximum((v - mb["ret"]) ** 2, (v_cl - mb["ret"]) ** 2))
        ent = jnp.mean(A.entropy(logits))
        loss = pg + cfg.vf * vf - cfg.ent * ent

        # Behavioral cloning on expert combat actions
        bc_loss = -jnp.mean(A.log_prob(logits, mb["exp_acts"]))
        loss = loss + cfg.w_bc * bc_loss

        use = tuple(k for k, w_ in (("map", cfg.w_map), ("geo", cfg.w_geo), ("probe", cfg.w_probe), ("fut", cfg.w_fut)) if w_ > 0)
        aux = A.aux_heads(params, hs, A.act_onehot(mb["acts"]), use)
        Tm = hs.shape[0]
        zero = jnp.float32(0.0)
        map_l = jnp.mean(optax.sigmoid_binary_cross_entropy(aux["map"], mb["aux"]["map"].reshape(Tm, -1, E.MAP * E.MAP))) if "map" in use else zero
        geo_l = jnp.mean((aux["geo"] - mb["aux"]["geo"]) ** 2) if "geo" in use else zero
        probe_l = jnp.mean((aux["probe"] - mb["aux"]["pos"]) ** 2) if "probe" in use else zero
        probe_err = jnp.median(jnp.linalg.norm(aux["probe"] - mb["aux"]["pos"], axis=-1)) * 1000.0 if "probe" in use else zero
        patches = mb["patch"].astype(jnp.float32).reshape(Tm, -1, E.PATCH * E.PATCH)
        cs = jnp.cumsum(mb["done"].astype(jnp.int32), 0)
        cs = jnp.concatenate([jnp.zeros((1,) + cs.shape[1:], cs.dtype), cs], 0)
        fut_l = zero
        for k in (A.FUT_KS if "fut" in use else ()):
            tgt = jnp.concatenate([patches[k:], jnp.zeros((k,) + patches.shape[1:])], 0)
            t_idx = jnp.arange(Tm)
            ends = cs[jnp.minimum(t_idx + k, Tm)] - cs[t_idx]
            valid = ((t_idx + k < Tm)[:, None] & (ends == 0)).astype(jnp.float32)
            bce = jnp.mean(optax.sigmoid_binary_cross_entropy(aux[f"fut{k}"], tgt), -1)
            fut_l = fut_l + jnp.sum(bce * valid) / (jnp.sum(valid) + 1.0) / len(A.FUT_KS)
        loss = loss + cfg.w_map * map_l + cfg.w_fut * fut_l + cfg.w_geo * geo_l + cfg.w_probe * probe_l
        kl = jnp.mean((ratio - 1) - jnp.log(ratio))
        return loss, dict(pg=pg, vf=vf, ent=ent, bc=bc_loss, map=map_l, fut=fut_l, geo=geo_l, probe=probe_l,
                          probe_err_m=probe_err, kl=kl, clipfrac=jnp.mean(jnp.abs(ratio - 1) > cfg.clip))

    tx = optax.chain(optax.clip_by_global_norm(0.5), optax.adam(cfg.lr, eps=1e-5))

    @jax.jit
    def update(params, opt_state, traj, last_v, hc0, resetf0, key):
        adv, ret = gae(traj["r"], traj["v"], traj["done"], last_v)
        resetf = traj["resetf"].at[0].set(resetf0)
        data = dict(patch=traj["patch"], vec=traj["vec"], priv=traj["priv"], aux=traj["aux"], resetf=resetf,
                    acts=traj["acts"], exp_acts=traj["exp_acts"], logp=traj["logp"], v=traj["v"], done=traj["done"], adv=adv, ret=ret)
        MB = N // cfg.minibatches

        def epoch(c, k):
            params, opt_state = c
            perm = jax.random.permutation(k, N)

            def mb_step(c2, idx):
                params, opt_state = c2
                mb = jax.tree_util.tree_map(lambda x: x[:, idx], data)
                mb["hc0"] = (hc0[0][idx], hc0[1][idx])
                (_, met), g = jax.value_and_grad(loss_fn, has_aux=True)(params, mb)
                upd, opt_state = tx.update(g, opt_state, params)
                return (optax.apply_updates(params, upd), opt_state), met

            (params, opt_state), met = jax.lax.scan(mb_step, (params, opt_state), perm.reshape(cfg.minibatches, MB))
            return (params, opt_state), met

        (params, opt_state), met = jax.lax.scan(epoch, (params, opt_state), jax.random.split(key, cfg.epochs))
        met = jax.tree_util.tree_map(jnp.mean, met)
        var_y = jnp.var(ret)
        met["explained_var"] = 1 - jnp.var(ret - traj["v"]) / (var_y + 1e-8)
        return params, opt_state, met

    return first_carry, rollout, update, tx


def main():
    cfg = parse()
    A.configure(cfg.hidden, cfg.channels.split(","))
    print(f"🥊 BRAWLER / ENFORCER TRAINING: JAX on {jax.devices()}  envs={cfg.envs} rollout={cfg.rollout}")
    world = E.make_world(W.build())
    first_carry, rollout, update, tx = build_fns(world, cfg)
    key = jax.random.PRNGKey(cfg.seed)
    ckpt = os.path.join(HERE, "checkpoints", "fighter_latest.pkl")

    step0, hi = 0, cfg.cur_start
    hist, tier_stats = [], districts.get_district_stats_template()
    teacher_eps = cfg.teacher_eps

    if cfg.resume and os.path.exists(ckpt):
        d = pickle.load(open(ckpt, "rb"))
        params, opt_state = d["params"], d["opt_state"]
        step0 = d["meta"].get("step", 0)
        hi = d["meta"].get("cur_hi", cfg.cur_start)
        hist = d["meta"].get("history", [])
        tier_stats = d["meta"].get("tiers", tier_stats)
        print(f"Resumed brawler training from {ckpt} at step {step0:,}")
    elif os.path.exists(cfg.init_ckpt):
        d = pickle.load(open(cfg.init_ckpt, "rb"))
        params = d["params"]
        opt_state = tx.init(params)
        print(f"Warm-started from runner checkpoint {cfg.init_ckpt}")
    else:
        params = A.init(jax.random.fold_in(key, 1))
        opt_state = tx.init(params)
        print("Initialized new agent weights")

    def cur_of(hi):
        return E.Curriculum(lo=jnp.float32(0.4 * hi), hi=jnp.float32(hi), p_uniform=jnp.float32(0.35))

    carry = first_carry(jax.random.fold_in(key, 2), cur_of(hi))
    per_update = cfg.envs * cfg.rollout
    n_updates = max(1, (cfg.steps - step0) // per_update)
    t_start, steps_run = time.time(), 0
    recent = []
    best = -1e9

    for u in range(n_updates):
        key, k1 = jax.random.split(key)
        cur = cur_of(hi)
        carry, traj, last_v, hc0, resetf0 = rollout(params, carry, cur, jnp.float32(teacher_eps))
        teacher_eps = max(0.05, teacher_eps * cfg.teacher_decay)
        params, opt_state, met = update(params, opt_state, traj, last_v, hc0, resetf0, k1)
        met = {k: float(v) for k, v in jax.device_get(met).items()}
        info = jax.device_get(traj["info"])
        dmask = info["done"]
        eps = [dict(success=bool(info["success"][i]), dead=bool(info["dead"][i]),
                    ret=float(info["ep_ret"][i]), score=float(info["score"][i]), len=int(info["ep_len"][i]),
                    kills=float(info["kills"][i]), civ=float(info["civ_hits"][i]),
                    start_x=float(info["start_x"][i]), start_z=float(info["start_z"][i])) for i in zip(*np.nonzero(dmask))]
        recent = (recent + eps)[-2000:]
        for e in eps:
            d_name = districts.get_nearest_district(e["start_x"], e["start_z"])
            s = tier_stats[d_name]
            s["episodes"] += 1
            s["wins"] += int(e["success"])
            s["ret"] += e["ret"]

        steps_run += per_update
        step = step0 + steps_run
        el = time.time() - t_start
        sps = steps_run / el
        R = [e["ret"] for e in recent[-300:]] or [0.0]
        mean_r = float(np.mean(R)); best = max(best, mean_r)
        succ = float(np.mean([e["success"] for e in recent[-300:]])) if recent else 0.0
        deaths = float(np.mean([e["dead"] for e in recent[-300:]])) if recent else 0.0
        avg_kills = float(np.mean([e["kills"] for e in recent[-300:]])) if recent else 0.0
        avg_civ = float(np.mean([e["civ"] for e in recent[-300:]])) if recent else 0.0

        if u % 5 == 0 or u == n_updates - 1:
            print(f"[{step:>10,}] {sps:6.0f} sps | ret {mean_r:6.2f} kills {avg_kills:4.1f} civ_hits {avg_civ:4.2f} died {deaths:.2f} | "
                  f"pg {met['pg']:+.3f} vf {met['vf']:.3f} ent {met['ent']:.2f} bc {met['bc']:.3f} teach {teacher_eps:.2f} | "
                  f"map {met['map']:.3f} fut {met['fut']:.3f}", flush=True)

        if u % cfg.export_every == 0 or u == n_updates - 1:
            meta = dict(step=step, cur_hi=hi, history=hist, tiers=tier_stats, cfg=vars(cfg))
            os.makedirs(os.path.dirname(ckpt), exist_ok=True)
            with open(ckpt + ".tmp", "wb") as f:
                pickle.dump(dict(params=jax.device_get(params), opt_state=jax.device_get(opt_state), meta=meta), f)
            os.replace(ckpt + ".tmp", ckpt)

            from export import export
            export(params, os.path.join(ROOT, "ai_model_fighter.json"),
                   meta=dict(step=step, mode="fighter", avg_kills=round(avg_kills, 2), civ_hits=round(avg_civ, 2),
                             success_rate=round(succ, 3), tag="fighter"))

    print("🥊 Brawler / Enforcer training complete!")


if __name__ == "__main__":
    main()
