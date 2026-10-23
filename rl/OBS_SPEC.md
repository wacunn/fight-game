# Observation / action spec (obs_version 2)

This is the contract between `rl/env.py` (`observe`) and `ai_copilot.js` (`buildObservation`).
Both sides produce identical patches, vectors within float rounding, and identical logits.
obs_version 2 adds 3 fine-grained combat features per NPC (fine distance, jab reach, kick reach).
`ai_copilot.js` backwards-compatibly supports both obs_version 1 (93 floats) and obs_version 2 (111 floats).

## Frames

Game coordinates are (x, z) in metres, with yaw ψ as in `game.js`:

- forward f = (−sin ψ, −cos ψ)
- right r = (cos ψ, −sin ψ)
- turning right **decreases** ψ

"Ahead" and "right" of a world vector v are v·f and v·r. The policy never sees absolute (x, z).

## Patch (16×16, float 0/1)

The patch reads `ai_grid.js`: 1 m occupancy rasterized from `city.canMoveTo(x, z, 0.6, 1.7)`, 1 = blocked, and out of bounds = blocked.

- Cell (i, j) samples the world at `pos + ahead·f + right·r`.
- `ahead = (11.5 − i)·2 m`: row 0 is 23 m ahead, row 15 is 7 m behind.
- `right = (j − 7.5)·2 m`: ±15 m.
- The sample point is floored to the 1 m grid.

## Vector (111 floats in v2, 93 floats in v1)

| idx | feature |
|---|---|
| 0–7 | health/100, armor/50, rage/100, berserk (0/1), berserk_time/16, attack_cooldown/0.55, in_sanctuary (0/1), 1 |
| 8–11 | goal (mission crate): sin θ, cos θ, log1p(d)/7.5, min(d,10)/10 — θ = atan2(right, ahead), 0 = dead ahead |
| 12–14 | peace sanctuary centre: sin θ, cos θ, log1p(d)/7.5 |
| 15–18 | difficulty one-hot (easy, medium, hard, impossible) |
| 19–32 | previous action one-hot: move (6), turn (5), attack (3) |
| 33–110 | 6 nearest living people within 40 m, nearest first, 13 features each: present, ahead/40, right/40, dist/40, looks_civilian, robot, unmasked_snatcher, hp/maxHp, staggered, punching, min(dist, 6.0)/6.0, facing & in_jab_reach (<=3.5m), facing & in_kick_reach (<=4.2m). Empty slots are all zeros. |

A disguised snatcher has `looks_civilian = 1` until it is unmasked: by proximity (10 m), or by being hit.

## Actions (MultiDiscrete [6, 5, 3], decided at 10 Hz)

- **move**: none, forward, back, strafe left, strafe right, sprint-forward. Walk is 7 m/s, sprint 11.5 m/s. Berserk always sprints.
- **turn**: −0.5, −0.15, 0, +0.15, +0.5 rad, where positive = right. The game spreads each turn over the 0.1 s decision interval.
- **attack**: none, primary, kick. These map to the game's own `triggerAttack()` and `triggerQuickKick()`.
  - Primary becomes a glory kill if a staggered foe is within 4 m.
  - Either attack smashes the mission crate within 6.5 m.

## Episodes in the game

One mission is one episode. The copilot resets its LSTM whenever the mission target changes, and on death. With no active mission, the goal falls back to the sanctuary centre.
