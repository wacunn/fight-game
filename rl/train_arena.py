#!/usr/bin/env python3
"""
PPO-LSTM 1v1 Pure Boxing Arena Trainer ("Curriculum Stage 1").

Trains the brawler policy inside a dedicated 14m x 14m boxing ring against
hostile combatants (robots & snatchers).
Focuses 100% of gradient updates on:
  - Striking reach and spacing (jabbing, heavy kicks, countering)
  - Combat footwork (closing distance without sprint overshoot)
  - Glory kills on staggered enemies
  - Dodging incoming punches

Exports to:
  - rl/checkpoints/fighter_arena_latest.pkl (for warm-starting full-city training)
  - ai_model_fighter.json (playable in-game via AI Copilot 'Brawler' persona)
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
import arena as Ar
from export import export

ROOT = os.path.abspath(os.path.join(HERE, ".."))


def parse():
    ap = argparse.ArgumentParser(description="1v1 Pure Boxing Arena PPO Trainer")
    ap.add_argument("--envs", type=int, default=128, help="parallel arena environments")
    ap.add_argument("--rollout", type=int, default=64, help="rollout steps per update")
    ap.add_argument("--steps", type=int, default=3_000_000, help="total environment frames")
    ap.add_argument("--epochs", type=int, default=2, help="PPO epochs per update")
    ap.add_argument("--hidden", type=int, default=128, help="LSTM hidden units")
    ap.add_argument("--channels", default="8,16,16", help="conv channel widths")
    ap.add_argument("--minibatches", type=int, default=4, help="PPO minibatches")
    ap.add_argument("--lr", type=float, default=2.5e-4, help="Adam learning rate")
    ap.add_argument("--gamma", type=float, default=0.99, help="discount factor")
    ap.add_argument("--lam", type=float, default=0.95, help="GAE lambda")
    ap.add_argument("--clip", type=float, default=0.2, help="PPO clip epsilon")
    ap.add_argument("--ent", type=float, default=0.02, help="entropy bonus coefficient")
    ap.add_argument("--vf", type=float, default=0.5, help="value function loss coefficient")
    ap.add_argument("--w-bc", type=float, default=1.5, help="teacher imitation / behavioral cloning weight")
    ap.add_argument("--teacher-eps", type=float, default=0.6, help="initial teacher guidance probability")
    ap.add_argument("--teacher-decay", type=float, default=0.999, help="teacher guidance decay per update")
    ap.add_argument("--export-every", type=int, default=25, help="updates between model exports")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--resume", action="store_true", help="resume training from fighter_arena_latest.pkl")
    ap.add_argument("--init-ckpt", default=None, help="optional initial checkpoint to warm-start from")
    return ap.parse_args()


def build_fns(cfg):
    N, T = cfg.envs, cfg.rollout
    vreset = jax.vmap(Ar.reset)
    vstep = jax.vmap(Ar.step)
    vobs = jax.vmap(Ar.observe)
    vpriv = jax.vmap(Ar.privileged)
    vexpert = jax.vmap(Ar.expert_act)

    def first_carry(key):
        k1, k2, k3 = jax.random.split(key, 3)
        st = vreset(jax.random.split(k1, N))
        spare = vreset(jax.random.split(k2, N))
        patch, vec = vobs(st)
        priv, aux = vpriv(st)
        z = jnp.zeros((N, A.H))
        return dict(
            st=st, hc=(z, z), patch=patch, vec=vec, priv=priv, aux=aux,
            resetf=jnp.ones(N, bool), spare=spare, key=k3
        )

    @jax.jit
    def rollout(params, carry, teacher_eps):
        def step_fn(c, t):
            key, k_act, k_env, k_sp, k_teach = jax.random.split(c["key"], 5)
            # Spare states for instant O(1) resets
            spare = jax.lax.cond(
                t % 32 == 0,
                lambda _: vreset(jax.random.split(k_sp, N)),
                lambda _: c["spare"],
                None
            )
            m = c["resetf"][:, None]
            hc = (jnp.where(m, 0.0, c["hc"][0]), jnp.where(m, 0.0, c["hc"][1]))
            h, hc = A.lstm(params, A.encode(params, c["patch"], c["vec"]), hc)
            logits, v = A.heads(params, h, c["priv"])
            acts, logp = A.sample(k_act, logits)

            exp_acts = vexpert(c["st"])
            teach_mask = jax.random.uniform(k_teach, (N,)) < teacher_eps
            exec_acts = jnp.where(teach_mask[:, None], exp_acts, acts)
            exec_logp = jnp.where(teach_mask, A.log_prob(logits, exp_acts), logp)

            nst, r, done, info = vstep(c["st"], exec_acts, jax.random.split(k_env, N))
            tp, tv = vobs(nst)
            tpriv, _ = vpriv(nst)
            th, _ = A.lstm(params, A.encode(params, tp, tv), hc)
            _, v_term = A.heads(params, th, tpriv)
            r = r + cfg.gamma * jnp.where(info["timeout"], jax.lax.stop_gradient(v_term), 0.0)

            # Instant reset on bout completion
            nst = jax.tree_util.tree_map(
                lambda a, b: jnp.where(done.reshape((-1,) + (1,) * (a.ndim - 1)), a, b),
                spare, nst
            )
            patch, vec = vobs(nst)
            priv, aux = vpriv(nst)
            tr = dict(
                patch=c["patch"].astype(jnp.uint8), vec=c["vec"], priv=c["priv"], aux=c["aux"],
                resetf=c["resetf"], acts=exec_acts, exp_acts=exp_acts, logp=exec_logp,
                v=v, r=r, done=done, info=info
            )
            nc = dict(st=nst, hc=hc, patch=patch, vec=vec, priv=priv, aux=aux, resetf=done, spare=spare, key=key)
            return nc, tr

        hc0 = carry["hc"]
        resetf0 = carry["resetf"]
        carry, traj = jax.lax.scan(step_fn, carry, jnp.arange(T))
        m = carry["resetf"][:, None]
        hc = (jnp.where(m, 0.0, carry["hc"][0]), jnp.where(m, 0.0, carry["hc"][1]))
        h, _ = A.lstm(params, A.encode(params, carry["patch"], carry["vec"]), hc)
        _, last_v = A.heads(params, h, carry["priv"])
        return carry, traj, last_v, hc0, resetf0

    @jax.jit
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
        surr1 = ratio * mb["adv"]
        surr2 = jnp.clip(ratio, 1.0 - cfg.clip, 1.0 + cfg.clip) * mb["adv"]
        pi_loss = -jnp.mean(jnp.minimum(surr1, surr2))

        vf_loss = 0.5 * jnp.mean((v - mb["ret"]) ** 2)
        ent = jnp.mean(A.entropy(logits))

        # Imitation / behavioral cloning loss against expert
        bc_loss = -jnp.mean(A.log_prob(logits, mb["exp_acts"]))
        w_bc = mb.get("w_bc", jnp.float32(cfg.w_bc))

        total = pi_loss + cfg.vf * vf_loss - cfg.ent * ent + w_bc * bc_loss
        return total, dict(pi=pi_loss, vf=vf_loss, ent=ent, bc=bc_loss, total=total)

    tx = optax.chain(optax.clip_by_global_norm(0.5), optax.adam(cfg.lr))

    @jax.jit
    def update_step(params, opt_state, mb):
        grads, stats = jax.grad(loss_fn, has_aux=True)(params, mb)
        updates, opt_state = tx.update(grads, opt_state, params)
        params = optax.apply_updates(params, updates)
        return params, opt_state, stats

    return dict(first_carry=first_carry, rollout=rollout, gae=gae, update_step=update_step, tx=tx)


def train():
    cfg = parse()
    A.configure(hidden=cfg.hidden, channels=cfg.channels.split(","))
    fns = build_fns(cfg)

    ckpt_dir = os.path.join(HERE, "checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    ckpt = os.path.join(ckpt_dir, "fighter_arena_latest.pkl")

    key = jax.random.PRNGKey(cfg.seed)
    k_init, k_run = jax.random.split(key)
    params = A.init(k_init)
    tx = fns["tx"]
    opt_state = tx.init(params)

    step0 = 0
    hist = []
    teacher_eps = cfg.teacher_eps

    # Resume or warm-start if available
    if cfg.resume and os.path.exists(ckpt):
        d = pickle.load(open(ckpt, "rb"))
        params = d["params"]
        opt_state = d["opt_state"]
        step0 = d["meta"].get("step", 0)
        hist = d["meta"].get("history", [])
        teacher_eps = d["meta"].get("teacher_eps", cfg.teacher_eps)
        print(f"🥊 Resumed Arena training from {ckpt} at step {step0:,}")
    elif cfg.init_ckpt and os.path.exists(cfg.init_ckpt):
        d = pickle.load(open(cfg.init_ckpt, "rb"))
        # Load trunk parameters where shapes match
        loaded = 0
        for k in d["params"]:
            if k in params and d["params"][k]["w"].shape == params[k]["w"].shape:
                params[k] = d["params"][k]
                loaded += 1
        opt_state = tx.init(params)
        print(f"🥊 Warm-started {loaded} parameter layers from {cfg.init_ckpt}")
    else:
        print("🥊 Starting 1v1 Arena training from scratch (tabula rasa).")

    carry = fns["first_carry"](k_run)
    batch_sz = cfg.envs * cfg.rollout
    mbsz = cfg.envs // cfg.minibatches
    n_updates = (cfg.steps - step0) // batch_sz

    print(f"\n========================================================")
    print(f"  🥊 1v1 PURE BOXING ARENA PPO TRAINING")
    print(f"  Envs: {cfg.envs}  Rollout: {cfg.rollout}  Batch: {batch_sz}")
    print(f"  Target Steps: {cfg.steps:,}  Initial Step: {step0:,}")
    print(f"  Teacher Epsilon: {teacher_eps:.3f} (decay: {cfg.teacher_decay})")
    print(f"========================================================\n")

    t0 = time.time()
    steps_accum = step0

    for upd in range(1, n_updates + 1):
        step = step0 + upd * batch_sz
        t_upd0 = time.time()

        # 1. Rollout
        carry, traj, last_v, hc0, resetf0 = fns["rollout"](params, carry, teacher_eps)
        adv, ret = fns["gae"](traj["r"], traj["v"], traj["done"], last_v)
        adv = (adv - jnp.mean(adv)) / (jnp.std(adv) + 1e-6)

        # 2. PPO Mini-batch updates
        cur_w_bc = cfg.w_bc * max(0.01, teacher_eps / max(1e-4, cfg.teacher_eps))
        mb_base = dict(
            patch=traj["patch"], vec=traj["vec"], priv=traj["priv"],
            resetf=traj["resetf"], acts=traj["acts"], exp_acts=traj["exp_acts"],
            logp=traj["logp"], adv=adv, ret=ret
        )
        stats_list = []
        for _ in range(cfg.epochs):
            perm = np.random.permutation(cfg.envs)
            for mb_i in range(cfg.minibatches):
                idx = perm[mb_i * mbsz:(mb_i + 1) * mbsz]
                mb = {k: v[:, idx] for k, v in mb_base.items()}
                mb["hc0"] = (hc0[0][idx], hc0[1][idx])
                mb["w_bc"] = jnp.float32(cur_w_bc)
                params, opt_state, stats = fns["update_step"](params, opt_state, mb)
                stats_list.append(stats)

        # 3. Track metrics
        info = traj["info"]
        dones = info["done"]
        n_dones = int(jnp.sum(dones))
        win_rate = float(jnp.sum(info["success"]) / max(1, n_dones)) if n_dones > 0 else 0.0
        loss_rate = float(jnp.sum(info["dead"]) / max(1, n_dones)) if n_dones > 0 else 0.0
        mean_ret = float(jnp.mean(traj["r"]))
        hits_sum = int(jnp.sum(info["hits_landed"]))

        # Decay teacher epsilon toward pure self-play
        teacher_eps = max(0.02, teacher_eps * cfg.teacher_decay)

        fps = batch_sz / max(1e-4, time.time() - t_upd0)
        total_time = time.time() - t0

        pi_l = float(np.mean([s["pi"] for s in stats_list]))
        vf_l = float(np.mean([s["vf"] for s in stats_list]))
        bc_l = float(np.mean([s["bc"] for s in stats_list]))

        if upd % 5 == 0 or upd == 1:
            print(f"[{upd:04d}/{n_updates:04d}] step {step:8,d} | "
                  f"win: {win_rate * 100:5.1f}% | loss: {loss_rate * 100:4.1f}% | "
                  f"hits: {hits_sum:4d} | ret: {mean_ret:5.2f} | "
                  f"teach: {teacher_eps:.2f} | bc: {bc_l:4.2f} | {fps:5.0f} fps")

        # 4. Checkpoint & Export
        if upd % cfg.export_every == 0 or upd == n_updates:
            meta = dict(
                step=step, win_rate=round(win_rate, 3), loss_rate=round(loss_rate, 3),
                teacher_eps=round(teacher_eps, 3), tag="arena_1v1"
            )
            pickle.dump(dict(params=params, opt_state=opt_state, meta=meta), open(ckpt, "wb"))
            # Export to both ai_model_fighter.json and ai_model.json
            fighter_json = os.path.join(ROOT, "ai_model_fighter.json")
            export(params, fighter_json, meta=meta)
            print(f"  💾 Saved checkpoint {ckpt}")
            print(f"  🚀 Exported {fighter_json} (win rate: {win_rate * 100:.1f}%)")


if __name__ == "__main__":
    train()
