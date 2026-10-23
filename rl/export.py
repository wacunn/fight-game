"""
Export the policy half of the network (encoder + LSTM + policy head) to ai_model.json for the game.
Weights are float16, base64, row-major; shapes are given so the JS side can index them.

  python3 rl/export.py [rl/checkpoints/latest.pkl] [ai_model.json]
"""
import base64
import json
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import env as E  # noqa: E402

SPEC = dict(
    obs_version=2, dt=E.DT, patch=E.PATCH, patch_cell=E.PATCH_CELL, patch_row0=E.PATCH_ROW0,
    vec_dim=E.VEC_DIM, k_obs=E.K_OBS, npc_feats=E.NPC_FEATS, npc_range=E.NPC_RANGE,
    jab_range=float(E.JAB["range"]), kick_range=float(E.KICK["range"]),
    act_dims=list(E.ACT_DIMS), turns=[float(t) for t in np.asarray(E.TURNS)],
    kick_cooldown=float(E.KICK["cooldown"]), hidden=256,
)


def _tensors(params):
    out = {}
    def put(name, arr):
        a = np.asarray(arr, np.float32)
        out[name] = dict(shape=list(a.shape), data=base64.b64encode(a.astype("<f2").tobytes()).decode())
    for k in ("c1", "c2", "c3", "pd", "vd", "fd", "pi1", "pi2"):
        put(k + ".w", params[k]["w"]); put(k + ".b", params[k]["b"])
    put("lstm.wx", params["lstm"]["wx"]); put("lstm.wh", params["lstm"]["wh"]); put("lstm.b", params["lstm"]["b"])
    return out


def export(params, path, meta=None):
    spec = dict(SPEC, hidden=int(np.asarray(params["lstm"]["wh"]).shape[0]),
                channels=[int(np.asarray(params[k]["w"]).shape[-1]) for k in ("c1", "c2", "c3")])
    doc = dict(version=2, arch="ego-cnn-lstm-v1", dtype="f16", spec=spec, meta=meta or {}, tensors=_tensors(params))
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(doc, f, separators=(",", ":"))
    os.replace(tmp, path)
    return path


if __name__ == "__main__":
    ck = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "checkpoints", "latest.pkl")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "ai_model.json")
    d = pickle.load(open(ck, "rb"))
    export(d["params"], out, meta=dict(step=d["meta"]["step"], curriculum_m=d["meta"].get("cur_hi")))
    print(f"exported {out} ({os.path.getsize(out) / 1e6:.2f} MB)")
