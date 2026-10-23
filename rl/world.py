"""
World precompute for the Toronto RL env.

Everything here is derived from ai_grid.js, which tools/export_ai_grid.js rasterizes from the
game's own street-level collision (city.canMoveTo, player radius 0.6, eye height 1.7). The env and
the in-game copilot read the same grid, so the agent trains in the same city it plays in.

Produces (cached to rl/cache/world_<hash>.npz):
  occ      (H, W)  uint8   1 m occupancy, 1 = blocked              [rows = z, cols = x]
  pool6    (H6,W6) float16 6 m block-mean occupancy (map-reconstruction aux target)
  free2    (H2,W2) bool    2 m cells usable by the geodesic planner (largest component)
  fields   (G,H2,W2) float16  geodesic distance (m) from every 2 m cell to goal g (inf = unreachable)
  goals    (G, 2)  float32 goal positions (x, z); the first ones are the game's mission landmarks
  spawn_xz (S, 2)  float32 random free 1 m positions in the main component (spawn candidates)
"""
import base64
import hashlib
import json
import os
import sys

import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

HERE = os.path.dirname(os.path.abspath(__file__))


def load_grid(path=None):
    path = path or os.path.join(HERE, "..", "ai_grid.js")
    s = open(path, encoding="utf-8").read()
    g = json.loads(s[s.index("{"): s.rindex("}") + 1])
    raw = np.frombuffer(base64.b64decode(g["bits"]), np.uint8)
    occ = np.unpackbits(raw, bitorder="little")[: g["w"] * g["h"]].reshape(g["h"], g["w"])
    return g, occ.astype(np.uint8), hashlib.sha1(g["bits"].encode()).hexdigest()[:10]


def build(grid_path=None, n_goals=96, seed=0, verbose=True):
    meta, occ, h = load_grid(grid_path)
    cache = os.path.join(HERE, "cache", f"world_{h}_{n_goals}_{seed}.npz")
    if os.path.exists(cache):
        d = dict(np.load(cache, allow_pickle=False))
        d["meta"] = meta
        return d
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    rng = np.random.default_rng(seed)
    H, W = occ.shape
    x0, z0 = meta["x0"], meta["z0"]

    # main walkable component at 1 m
    lab, _ = ndimage.label(occ == 0)
    sizes = np.bincount(lab.ravel()); sizes[0] = 0
    main1 = lab == sizes.argmax()

    # 2 m planner cells: usable if any of their 1 m cells is in the main component
    H2, W2 = H // 2, W // 2
    free2 = main1[: H2 * 2, : W2 * 2].reshape(H2, 2, W2, 2).any(axis=(1, 3))
    lab2, _ = ndimage.label(free2, structure=np.ones((3, 3)))
    s2 = np.bincount(lab2.ravel()); s2[0] = 0
    free2 = lab2 == s2.argmax()

    # 6 m pooled occupancy for the cognitive-map auxiliary target
    H6, W6 = H // 6, W // 6
    pool6 = occ[: H6 * 6, : W6 * 6].reshape(H6, 6, W6, 6).mean(axis=(1, 3)).astype(np.float16)

    # goal set: mission landmarks (snapped to the nearest free 2 m cell) + farthest-point spread
    fz, fx = np.nonzero(free2)
    cell_xy = np.stack([x0 + fx * 2 + 1.0, z0 + fz * 2 + 1.0], 1)
    goals = []
    for m in meta.get("missions", []):
        d = np.hypot(cell_xy[:, 0] - m["x"], cell_xy[:, 1] - m["z"])
        goals.append(cell_xy[d.argmin()])
    goals = list(goals)
    cand = cell_xy[rng.choice(len(cell_xy), 20000, replace=False)]
    dmin = np.full(len(cand), np.inf)
    for gpt in goals:
        dmin = np.minimum(dmin, np.hypot(cand[:, 0] - gpt[0], cand[:, 1] - gpt[1]))
    while len(goals) < n_goals:
        k = dmin.argmax() if goals else 0
        goals.append(cand[k])
        dmin = np.minimum(dmin, np.hypot(cand[:, 0] - cand[k, 0], cand[:, 1] - cand[k, 1]))
    goals = np.array(goals, np.float32)

    # geodesic fields (multi-source Dijkstra, one source per goal)
    Gr, idx = _graph_safe(free2)
    gi = ((goals[:, 1] - z0) // 2).astype(int), ((goals[:, 0] - x0) // 2).astype(int)
    src = idx[gi[0], gi[1]]
    assert (src >= 0).all(), "goal snapped outside planner graph"
    if verbose:
        print(f"[world] grid {W}x{H}, planner {W2}x{H2} ({free2.sum()} cells), {len(goals)} goals: running Dijkstra...", file=sys.stderr)
    D = dijkstra(Gr, directed=False, indices=src)            # (G, n_free)
    fields = np.full((len(goals), H2, W2), np.inf, np.float32)
    fields[:, free2] = D
    fields = fields.astype(np.float16)

    # spawn candidates: random 1 m cell centres in the main component, away from the map edge
    sz, sx = np.nonzero(main1)
    keep = (sx > 20) & (sx < W - 20) & (sz > 20) & (sz < H - 20)
    pick = rng.choice(keep.sum(), 200000, replace=False)
    spawn_xz = np.stack([x0 + sx[keep][pick] + 0.5, z0 + sz[keep][pick] + 0.5], 1).astype(np.float32)

    out = dict(occ=occ, pool6=pool6, free2=free2, fields=fields, goals=goals, spawn_xz=spawn_xz)
    np.savez_compressed(cache, **out)
    out["meta"] = meta
    if verbose:
        print(f"[world] cached -> {cache}", file=sys.stderr)
    return out


def _graph_safe(free):
    """Clean 8-connected graph, no corner cutting (diagonal only if both orthogonals are free)."""
    H, W = free.shape
    idx = -np.ones((H, W), np.int64)
    idx[free] = np.arange(free.sum())
    R, C, Wt = [], [], []

    def add(a_sl, b_sl, cost, extra=None):
        a = idx[a_sl]; b = idx[b_sl]
        m = (a >= 0) & (b >= 0)
        if extra is not None:
            m &= extra
        R.append(a[m]); C.append(b[m]); Wt.append(np.full(m.sum(), cost, np.float64))

    add((slice(None), slice(0, W - 1)), (slice(None), slice(1, W)), 2.0)            # east
    add((slice(0, H - 1), slice(None)), (slice(1, H), slice(None)), 2.0)            # south
    d = 2.0 * 2 ** 0.5
    # south-east: (z,x)->(z+1,x+1) needs (z,x+1) and (z+1,x)
    add((slice(0, H - 1), slice(0, W - 1)), (slice(1, H), slice(1, W)), d,
        free[0:H - 1, 1:W] & free[1:H, 0:W - 1])
    # south-west: (z,x)->(z+1,x-1) needs (z,x-1) and (z+1,x)
    add((slice(0, H - 1), slice(1, W)), (slice(1, H), slice(0, W - 1)), d,
        free[0:H - 1, 0:W - 1] & free[1:H, 1:W])
    r = np.concatenate(R); c = np.concatenate(C); w = np.concatenate(Wt)
    n = int(free.sum())
    Gm = coo_matrix((np.concatenate([w, w]), (np.concatenate([r, c]), np.concatenate([c, r]))), shape=(n, n)).tocsr()
    return Gm, idx


if __name__ == "__main__":
    import time
    t = time.time()
    w = build()
    f = w["fields"].astype(np.float32)
    print(f"built in {time.time() - t:.1f}s; goals {w['goals'].shape}; finite field frac {np.isfinite(f[0]).mean():.3f}; "
          f"max geodesic {np.nanmax(np.where(np.isfinite(f), f, np.nan)):.0f} m; fields {w['fields'].nbytes / 1e6:.0f} MB")
