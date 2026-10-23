#!/usr/bin/env python3
"""
Evaluate a checkpoint at fixed start->goal geodesic distances (no curriculum), sampling actions
exactly as in training.

    python3 rl/eval.py [rl/checkpoints/latest.pkl] [--episodes 64]

Per band it reports:
  - success, death and timeout rates;
  - efficiency: shortest path / distance actually walked, over successful episodes (1.0 = perfect route);
  - kills and civilian hits per episode;
  - the memory probe's median position error in metres.
"""
import argparse
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("JAX_PLATFORMS", "cpu")
import jax
import jax.numpy as jnp
import numpy as np

import agent as A
import env as E
import world as W

BANDS = [(30, 80), (80, 200), (200, 400), (400, 800), (800, 1400), (1400, 2500)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ckpt", nargs="?", default=os.path.join(HERE, "checkpoints", "latest.pkl"))
    ap.add_argument("--episodes", type=int, default=64)
    ap.add_argument("--seed", type=int, default=123)
    a = ap.parse_args()
    d = pickle.load(open(a.ckpt, "rb")); params = d["params"]
    A.configure(int(np.asarray(params["lstm"]["wh"]).shape[0]), [int(np.asarray(params[k]["w"]).shape[-1]) for k in ("c1", "c2", "c3")])
    world = E.make_world(W.build(verbose=False))
    N = a.episodes
    print(f"checkpoint step {d['meta']['step']:,}  (trained curriculum up to {d['meta']['cur_hi']:.0f} m)")
    print(f"{'band (m)':>12} {'success':>8} {'died':>6} {'timeout':>8} {'effic.':>7} {'kills':>6} {'civ':>5} {'probe m':>8}")

    @jax.jit
    def run(key, cur):
        st = jax.vmap(lambda k: E.reset(world, k, cur))(jax.random.split(key, N))
        z = jnp.zeros((N, A.H))

        def body(c, _):
            st, hc, alive, walked, done_info, key, perr = c
            key, ka, ke = jax.random.split(key, 3)
            patch, vec = jax.vmap(lambda s: E.observe(world, s))(st)
            priv, aux = jax.vmap(lambda s: E.privileged(world, s))(st)
            h, hc = A.lstm(params, A.encode(params, patch, vec), hc)
            logits, _ = A.heads(params, h, priv)
            probe = A.aux_heads(params, h[None], jnp.zeros((1, N, A.N_ACT)), use=("probe",))["probe"][0]
            err = jnp.linalg.norm(probe - aux["pos"], axis=-1) * 1000.0
            acts, _ = A.sample(ka, logits)
            nst, r, done, info = jax.vmap(lambda s, a_, k: E.step(world, s, a_, k, cur, 0.995))(st, acts, jax.random.split(ke, N))
            walked = walked + jnp.where(alive, jnp.linalg.norm(nst.pos - st.pos, axis=-1), 0.0)
            first = alive & done
            done_info = jax.tree_util.tree_map(lambda old, new: jnp.where(first, new, old), done_info, info)
            perr = perr + jnp.where(alive, err, 0.0)
            return (nst, hc, alive & ~done, walked, done_info, key, perr), err

        _, _, _, info0 = jax.vmap(lambda s, a_, k: E.step(world, s, a_, k, cur, 0.995))(
            st, jnp.zeros((N, 3), jnp.int32), jax.random.split(key, N))
        info0 = jax.tree_util.tree_map(jnp.zeros_like, info0)
        c0 = (st, (z, z), jnp.ones(N, bool), jnp.zeros(N), info0, key, jnp.zeros(N))
        (st, _, alive, walked, info, _, perr), errs = jax.lax.scan(body, c0, None, length=4000)
        return info, walked, st.geo0, alive, errs

    for lo, hi in BANDS:
        cur = E.Curriculum(jnp.float32(lo), jnp.float32(hi), jnp.float32(0.0))
        info, walked, geo0, still, errs = jax.device_get(run(jax.random.PRNGKey(a.seed + lo), cur))
        s = info["success"].astype(bool)
        eff = np.median(geo0[s] / np.maximum(walked[s], 1e-3)) if s.any() else float("nan")
        print(f"{lo:5d}-{hi:<5d}  {s.mean():8.2f} {info['dead'].mean():6.2f} {info['timeout'].mean():8.2f} {eff:7.2f} "
              f"{info['kills'].mean():6.2f} {info['civ_hits'].mean():5.2f} {np.median(errs[:200]):8.0f}")


if __name__ == "__main__":
    main()
