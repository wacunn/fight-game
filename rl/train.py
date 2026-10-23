#!/usr/bin/env python3
"""
PPO-LSTM + auxiliary losses on the egocentric Toronto env (all JAX: env, rollout and update are jitted).

    python3 rl/train.py                                 # defaults (Mac: ~256 envs)
    python3 rl/train.py --envs 512 --steps 200_000_000
    python3 rl/train.py --w-map 0 --w-fut 0 --w-geo 0   # pure PPO baseline (ablation)
    python3 rl/train.py --resume                        # continue from rl/checkpoints/latest.pkl

Auxiliary losses (all optional, weights on the CLI):
    --w-fut   action-conditioned prediction of the egocentric view 1, 4 and 8 steps ahead (predictive coding)
    --w-map   reconstruct a 144 m egocentric occupancy map from memory (only 32 m is ever visible)
    --w-geo   regress geodesic distance + shortest-path direction to the goal (privileged teacher signal;
              set to 0 if you want the representation shaped only by self-supervised losses)
    probe     linear decoder of absolute position from stop_grad(h): a *diagnostic* of whether a map
              emerged in memory; it never trains the trunk.
Reward uses potential-based geodesic shaping (Ng et al. 1999: F = gamma*Phi(s') - Phi(s)), which leaves
the optimal policy unchanged. The critic additionally sees privileged state (asymmetric actor-critic).

Writes train_status.json/.js (dashboard.html), rl/checkpoints/latest.pkl, and ai_model.json (for the game).
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
    ap.add_argument("--envs", type=int, default=256)
    ap.add_argument("--rollout", type=int, default=128)
    ap.add_argument("--steps", type=int, default=100_000_000)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--hidden", type=int, default=128, help="LSTM width")
    ap.add_argument("--channels", default="8,16,16", help="conv widths")
    ap.add_argument("--minibatches", type=int, default=4)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--gamma", type=float, default=0.998)
    ap.add_argument("--lam", type=float, default=0.95)
    ap.add_argument("--clip", type=float, default=0.2)
    ap.add_argument("--ent", type=float, default=0.01)
    ap.add_argument("--vf", type=float, default=0.5)
    ap.add_argument("--w-fut", type=float, default=0.5)
    ap.add_argument("--w-map", type=float, default=0.5)
    ap.add_argument("--w-geo", type=float, default=0.25)
    ap.add_argument("--w-probe", type=float, default=1.0)
    ap.add_argument("--w-bc", type=float, default=1.0, help="teacher behavioral cloning / imitation loss weight")
    ap.add_argument("--teacher-eps", type=float, default=0.5, help="initial fraction of teacher-guided envs")
    ap.add_argument("--teacher-decay", type=float, default=0.9995, help="teacher guidance decay per update")
    ap.add_argument("--cur-start", type=float, default=60.0, help="initial max start->goal geodesic distance (m)")
    ap.add_argument("--cur-max", type=float, default=2500.0)
    ap.add_argument("--export-every", type=int, default=50, help="updates between ai_model.json exports")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--tag", default="")
    return ap.parse_args()


# ----------------------------------------------------------------------------- jitted pieces
def build_fns(world, cfg):
    N, T = cfg.envs, cfg.rollout
    vreset = jax.vmap(lambda k, cur: E.reset(world, k, cur), in_axes=(0, None))
    vstep = jax.vmap(lambda s, a, k, cur: E.step(world, s, a, k, cur, cfg.gamma), in_axes=(0, 0, 0, None))
    vobs = jax.vmap(lambda s: E.observe(world, s))
    vpriv = jax.vmap(lambda s: E.privileged(world, s))
    vexpert = jax.vmap(lambda s: E.expert_act(world, s))

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
            # time-limit truncation is not termination: bootstrap with V(final state) before swapping in a spare
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

        # Behavioral cloning on expert navigation & combat actions
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
        # future-view prediction: target patch_{t+k}, valid iff t+k < T and no episode end in [t, t+k-1]
        patches = mb["patch"].astype(jnp.float32).reshape(Tm, -1, E.PATCH * E.PATCH)
        cs = jnp.cumsum(mb["done"].astype(jnp.int32), 0)
        cs = jnp.concatenate([jnp.zeros((1,) + cs.shape[1:], cs.dtype), cs], 0)       # cs[t] = dones in [0, t-1]
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


# ----------------------------------------------------------------------------- 30 Toronto Districts
TIERS = districts.DISTRICT_NAMES


def save_ckpt(path, params, opt_state, meta):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "wb") as f:
        pickle.dump(dict(params=jax.device_get(params), opt_state=jax.device_get(opt_state), meta=meta), f)
    os.replace(path + ".tmp", path)


def main():
    cfg = parse()
    A.configure(cfg.hidden, cfg.channels.split(","))
    print(f"JAX {jax.__version__} on {jax.devices()}  envs={cfg.envs} rollout={cfg.rollout}")
    world = E.make_world(W.build())
    first_carry, rollout, update, tx = build_fns(world, cfg)
    key = jax.random.PRNGKey(cfg.seed)
    ckpt = os.path.join(HERE, "checkpoints", "latest.pkl")

    params = A.init(jax.random.fold_in(key, 1))
    opt_state = tx.init(params)
    step0, hi = 0, cfg.cur_start
    hist, tier_stats = [], districts.get_district_stats_template()
    teacher_eps = cfg.teacher_eps
    if cfg.resume and os.path.exists(ckpt):
        d = pickle.load(open(ckpt, "rb"))
        params, opt_state = d["params"], d["opt_state"]
        step0, hi = d["meta"]["step"], d["meta"]["cur_hi"]
        hist, tier_stats = d["meta"].get("history", []), d["meta"].get("tiers", tier_stats)
        print(f"resumed at step {step0:,}, curriculum {hi:.0f} m")

    def cur_of(hi):
        return E.Curriculum(lo=jnp.float32(0.4 * hi), hi=jnp.float32(hi), p_uniform=jnp.float32(0.25))

    carry = first_carry(jax.random.fold_in(key, 2), cur_of(hi))
    per_update = cfg.envs * cfg.rollout
    n_updates = max(1, (cfg.steps - step0) // per_update)
    t_start, steps_run = time.time(), 0
    recent = []                                  # recent finished episodes (dicts)
    best = -1e9
    for u in range(n_updates):
        t0 = time.time()
        key, k1 = jax.random.split(key)
        cur = cur_of(hi)
        carry, traj, last_v, hc0, resetf0 = rollout(params, carry, cur, jnp.float32(teacher_eps))
        teacher_eps = max(0.05, teacher_eps * cfg.teacher_decay)
        params, opt_state, met = update(params, opt_state, traj, last_v, hc0, resetf0, k1)
        met = {k: float(v) for k, v in jax.device_get(met).items()}
        info = jax.device_get(traj["info"])
        dmask = info["done"]
        eps = [dict(success=bool(info["success"][i]), dead=bool(info["dead"][i]), geo0=float(info["geo0"][i]),
                    ret=float(info["ep_ret"][i]), score=float(info["score"][i]), len=int(info["ep_len"][i]), kills=float(info["kills"][i]),
                    civ=float(info["civ_hits"][i]),
                    start_x=float(info["start_x"][i]), start_z=float(info["start_z"][i])) for i in zip(*np.nonzero(dmask))]
        recent = (recent + eps)[-2000:]
        for e in eps:
            d_name = districts.get_nearest_district(e["start_x"], e["start_z"])
            s = tier_stats[d_name]
            s["episodes"] += 1
            s["wins"] += int(e["success"])
            s["ret"] += e["ret"]
        # curriculum on episodes started inside the current band
        band = [e for e in recent[-400:] if e["geo0"] >= 0.4 * hi]
        if len(band) >= 96:
            sr = np.mean([e["success"] for e in band])
            if sr >= 0.70 and hi < cfg.cur_max:
                hi = min(cfg.cur_max, hi * 1.15); recent = [e for e in recent if e["geo0"] < 0.4 * hi]
            elif sr < 0.20 and hi > 40:
                hi = max(40.0, hi * 0.95)
        steps_run += per_update
        step = step0 + steps_run
        el = time.time() - t_start
        sps = steps_run / el
        R = [e["ret"] for e in recent[-300:]] or [0.0]
        mean_r = float(np.mean(R)); best = max(best, mean_r)
        succ = float(np.mean([e["success"] for e in recent[-300:]])) if recent else 0.0
        deaths = float(np.mean([e["dead"] for e in recent[-300:]])) if recent else 0.0
        if u % 5 == 0 or u == n_updates - 1:
            print(f"[{step:>11,}] {sps:7.0f} sps | ret {mean_r:6.2f} score {np.mean([e['score'] for e in recent[-300:]] or [0]):6.0f} succ {succ:.2f} died {deaths:.2f} | cur {hi:6.0f} m | "
                  f"pg {met['pg']:+.3f} vf {met['vf']:.3f} ent {met['ent']:.2f} bc {met['bc']:.3f} teach {teacher_eps:.2f} | "
                  f"map {met['map']:.3f} fut {met['fut']:.3f} geo {met['geo']:.3f} probe {met['probe_err_m']:5.0f} m", flush=True)
        hist.append(dict(step=step, reward=round(mean_r, 3), success=round(succ, 3), died=round(deaths, 3), cur_m=round(hi, 1),
                         policy_loss=round(met["pg"], 5), value_loss=round(met["vf"], 4), entropy_loss=round(-met["ent"], 4),
                         bc_loss=round(met["bc"], 4),
                         map_loss=round(met["map"], 4), fut_loss=round(met["fut"], 4), geo_loss=round(met["geo"], 4),
                         probe_err_m=round(met["probe_err_m"], 1), fps=round(sps, 1), time=round(el, 1)))
        hist = hist[-200:]
        if u % 5 == 0 or u == n_updates - 1:
            lb = []
            for d_name in districts.DISTRICT_NAMES:
                s = tier_stats[d_name]
                n_ = s["episodes"]
                wr = 100.0 * s["wins"] / max(1, n_)
                avg_r = s["ret"] / max(1, n_)
                if n_ < 5:
                    status_lbl = "Patrolling"
                elif wr >= 75:
                    status_lbl = "Mastered"
                elif wr >= 35:
                    status_lbl = "Combat Trained"
                else:
                    status_lbl = "Patrolling"
                lb.append(dict(district=d_name, episodes=n_, avg_reward=round(avg_r, 2), win_rate=f"{wr:.1f}%",
                               status=status_lbl))
            lb.sort(key=lambda x: -float(x["win_rate"][:-1]))
            for i, x in enumerate(lb):
                x["rank"] = i + 1
            status = dict(step=step, target_steps=cfg.steps, progress_pct=round(100.0 * step / cfg.steps, 2),
                          elapsed_seconds=round(el, 1), fps=round(sps, 1),
                          eta_hours=round((cfg.steps - step) / max(sps, 1) / 3600, 2), mean_reward=round(mean_r, 3),
                          best_reward=round(best, 3), success_rate=round(succ, 3), curriculum_m=round(hi, 1),
                          policy_loss=round(met["pg"], 5), value_loss=round(met["vf"], 4), entropy_loss=round(-met["ent"], 4),
                          total_loss=None, approx_kl=round(met["kl"], 5), explained_variance=round(met["explained_var"], 3),
                          aux=dict(bc=met["bc"], map=met["map"], fut=met["fut"], geo=met["geo"], probe_err_m=met["probe_err_m"]),
                          timestamp=time.strftime("%Y-%m-%d %H:%M:%S"), leaderboard=lb, history=hist)
            with open(os.path.join(ROOT, "train_status.json"), "w") as f:
                json.dump(status, f, indent=1)
            with open(os.path.join(ROOT, "train_status.js"), "w") as f:
                f.write("window.LIVE_TRAIN_STATUS = " + json.dumps(status) + ";\n")
        if u % cfg.export_every == 0 or u == n_updates - 1:
            meta = dict(step=step, cur_hi=hi, history=hist, tiers=tier_stats, cfg=vars(cfg))
            save_ckpt(ckpt, params, opt_state, meta)
            from export import export
            meta_exp = dict(step=step, curriculum_m=round(hi, 1), success_rate=round(succ, 3), tag=cfg.tag)
            export(params, os.path.join(ROOT, "ai_model.json"), meta=meta_exp)
            export(params, os.path.join(ROOT, "ai_model_runner.json"), meta=meta_exp)
            export(params, os.path.join(ROOT, "ai_model_fighter.json"), meta=meta_exp)
            try:
                import subprocess
                subprocess.run([sys.executable, os.path.join(ROOT, "tools", "bundle_play.py")], check=False)
            except Exception:
                pass
    print("done.")


if __name__ == "__main__":
    main()
