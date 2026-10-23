"""
Agent: egocentric encoder -> LSTM -> policy / value + auxiliary heads.  Plain JAX (dict params)
so the exported weights map 1:1 onto the JS forward pass in ai_copilot.js.

  patch 16x16 -> conv3x3/C1 s1 -> conv3x3/C2 s2 -> conv3x3/C3 s2 (pad 1, ReLU) -> 4x4xC3 -> dense 128
  vec 93      -> dense 128
  [256]       -> dense 256 -> LSTM H (gates i,f,g,o; c' = s(f)c + s(i)tanh(g); h' = s(o)tanh(c'))
  defaults: (C1,C2,C3) = (8,16,16), H = 128  -- sized so a MacBook CPU trains it; widen with --hidden/--channels
  policy:  h -> dense 128 -> 14 logits (move 6 | turn 5 | attack 3)          (exported to the game)
  value:   [h, privileged 6] -> dense 128 -> 1                               (asymmetric critic, train only)
  aux (train only, see AUX below):
    map    h -> 256 -> 24x24 logits     egocentric 144 m occupancy ("cognitive map" beyond the 32 m view)
    fut_k  [h, a_t..a_t+k-1] -> 256 -> 16x16 logits, k in (1,4,8)   action-conditioned prediction of the view
    geo    h -> 64 -> 3                 geodesic distance + shortest-path direction (privileged teacher)
    probe  stop_grad(h) -> 2            absolute position: diagnostic only, never shapes the trunk
"""
import jax
import jax.numpy as jnp
import numpy as np

from env import ACT_DIMS, MAP, PATCH, PRIV_DIM, VEC_DIM

H = 128                      # LSTM width   (set via configure())
CH = (8, 16, 16)             # conv widths  (set via configure())
ENC = 128                    # per-stream encoder width
N_ACT = sum(ACT_DIMS)


def configure(hidden=None, channels=None):
    global H, CH
    if hidden: H = int(hidden)
    if channels: CH = tuple(int(c) for c in channels)
FUT_KS = (1, 4, 8)


def _dense(key, nin, nout, scale=np.sqrt(2)):
    w = jax.nn.initializers.orthogonal(scale)(key, (nin, nout), jnp.float32)
    return {"w": w, "b": jnp.zeros(nout)}


def _conv(key, cin, cout):
    return {"w": jax.nn.initializers.lecun_normal()(key, (3, 3, cin, cout), jnp.float32), "b": jnp.zeros(cout)}


def init(key):
    with jax.default_device(jax.devices("cpu")[0]):
        ks = iter(jax.random.split(key, 32))
        p = {
            "c1": _conv(next(ks), 1, CH[0]), "c2": _conv(next(ks), CH[0], CH[1]), "c3": _conv(next(ks), CH[1], CH[2]),
            "pd": _dense(next(ks), 4 * 4 * CH[2], ENC), "vd": _dense(next(ks), VEC_DIM, ENC),
            "fd": _dense(next(ks), 2 * ENC, 2 * ENC),
            "lstm": {"wx": _dense(next(ks), 2 * ENC, 4 * H, 1.0)["w"], "wh": _dense(next(ks), H, 4 * H, 1.0)["w"],
                     "b": jnp.zeros(4 * H).at[H:2 * H].set(1.0)},      # forget-gate bias +1
            "pi1": _dense(next(ks), H, 128), "pi2": _dense(next(ks), 128, N_ACT, 0.01),
            "v1": _dense(next(ks), H + PRIV_DIM, 128), "v2": _dense(next(ks), 128, 1, 1.0),
            "map1": _dense(next(ks), H, 256), "map2": _dense(next(ks), 256, MAP * MAP, 0.1),
            "geo1": _dense(next(ks), H, 64), "geo2": _dense(next(ks), 64, 3, 0.1),
            "probe": _dense(next(ks), H, 2, 0.1),
        }
        for k in FUT_KS:
            p[f"fut{k}a"] = _dense(next(ks), H + k * N_ACT, 256)
            p[f"fut{k}b"] = _dense(next(ks), 256, PATCH * PATCH, 0.1)
    return jax.tree.map(lambda x: jax.device_put(x, jax.devices()[0]), p)


def _lin(p, x):
    return x @ p["w"] + p["b"]


def _conv2d(p, x, stride):
    y = jax.lax.conv_general_dilated(x, p["w"], (stride, stride), ((1, 1), (1, 1)),
                                     dimension_numbers=("NHWC", "HWIO", "NHWC"))
    return jax.nn.relu(y + p["b"])


def encode(p, patch, vec):
    """patch (B,16,16) float, vec (B,93) -> (B,256)."""
    x = patch[..., None]
    x = _conv2d(p["c1"], x, 1)
    x = _conv2d(p["c2"], x, 2)
    x = _conv2d(p["c3"], x, 2)
    x = x.reshape(x.shape[0], -1)                       # row-major (H, W, C)
    a = jax.nn.relu(_lin(p["pd"], x))
    b = jax.nn.relu(_lin(p["vd"], vec))
    return jax.nn.relu(_lin(p["fd"], jnp.concatenate([a, b], -1)))


def lstm(p, x, hc):
    h, c = hc
    z = x @ p["lstm"]["wx"] + h @ p["lstm"]["wh"] + p["lstm"]["b"]
    i, f, g, o = jnp.split(z, 4, -1)
    c = jax.nn.sigmoid(f) * c + jax.nn.sigmoid(i) * jnp.tanh(g)
    h = jax.nn.sigmoid(o) * jnp.tanh(c)
    return h, (h, c)


def heads(p, h, priv):
    logits = _lin(p["pi2"], jax.nn.relu(_lin(p["pi1"], h)))
    v = _lin(p["v2"], jax.nn.relu(_lin(p["v1"], jnp.concatenate([h, priv], -1))))[..., 0]
    return logits, v


def split_logits(logits):
    a, b = ACT_DIMS[0], ACT_DIMS[0] + ACT_DIMS[1]
    return logits[..., :a], logits[..., a:b], logits[..., b:]


def sample(key, logits):
    ks = jax.random.split(key, 3)
    parts = split_logits(logits)
    acts = jnp.stack([jax.random.categorical(k, l) for k, l in zip(ks, parts)], -1)
    return acts, log_prob(logits, acts)


def log_prob(logits, acts):
    parts = split_logits(logits)
    return sum(jnp.take_along_axis(jax.nn.log_softmax(l), acts[..., i:i + 1], -1)[..., 0] for i, l in enumerate(parts))


def entropy(logits):
    tot = 0.0
    for l in split_logits(logits):
        lp = jax.nn.log_softmax(l)
        tot = tot - jnp.sum(jnp.exp(lp) * lp, -1)
    return tot


def act_onehot(acts):
    return jnp.concatenate([jax.nn.one_hot(acts[..., i], d) for i, d in enumerate(ACT_DIMS)], -1)


def aux_heads(p, h, acts_onehot_seq, use=("map", "geo", "probe", "fut")):
    """h (T,B,H); acts_onehot_seq (T,B,N_ACT). Returns dict of predictions aligned at t.
    Only the heads named in `use` are computed (zero-weight losses cost nothing)."""
    out = {}
    if "map" in use:
        out["map"] = _lin(p["map2"], jax.nn.relu(_lin(p["map1"], h)))
    if "geo" in use:
        out["geo"] = _lin(p["geo2"], jax.nn.relu(_lin(p["geo1"], h)))
    if "probe" in use:
        out["probe"] = _lin(p["probe"], jax.lax.stop_gradient(h))
    if "fut" not in use:
        return out
    T = h.shape[0]
    for k in FUT_KS:
        # actions a_t .. a_{t+k-1}, zero-padded past the end of the rollout (those t are masked anyway)
        padded = jnp.concatenate([acts_onehot_seq, jnp.zeros((k,) + acts_onehot_seq.shape[1:])], 0)
        seq = jnp.concatenate([padded[j:j + T] for j in range(k)], -1)
        out[f"fut{k}"] = _lin(p[f"fut{k}b"], jax.nn.relu(_lin(p[f"fut{k}a"], jnp.concatenate([h, seq], -1))))
    return out


POLICY_KEYS = ("c1", "c2", "c3", "pd", "vd", "fd", "lstm", "pi1", "pi2")
