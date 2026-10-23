#!/usr/bin/env python3
"""
7-Hour Unified Brawler AI Training Pipeline.

Orchestrates the 7-hour curriculum:
  Phase 1 (1 hour): Hard 1v1 Arena
    - Teaches clean striking, heavy kicks, footwork without overshoot, glory kills
    - JIT GAE, dynamic BC imitation loss decay, teacher epsilon annealing
    - Saves checkpoint to rl/checkpoints/fighter_arena_latest.pkl
    
  Phase 2 (6 hours): Full Toronto City Enforcer
    - Warm-starts from the Phase 1 combat checkpoint
    - Full Toronto OSM map, multi-district roaming
    - Negative reward for hitting civilians (-10 jab, -25 KO)
    - Wall bump avoidance penalty
    - Live updates to train_status.json for dashboard monitoring
    - Exports to ai_model_fighter.json and snapshots hourly

Usage:
  python3 train_7h.py --hours 7.0
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable


def parse_args():
    ap = argparse.ArgumentParser(description="7-Hour Toronto Brawler AI Trainer")
    ap.add_argument("--hours", type=float, default=7.0, help="Total training duration in hours (default: 7.0)")
    ap.add_argument("--arena-hours", type=float, default=1.0, help="Arena phase duration in hours (default: 1.0)")
    ap.add_argument("--envs", type=int, default=128, help="Parallel vectorized environments (default: 128)")
    ap.add_argument("--rollout", type=int, default=64, help="Rollout steps per update (default: 64)")
    ap.add_argument("--resume", action="store_true", help="Resume from previous checkpoint if available")
    return ap.parse_args()


def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)


def run_phase_arena(target_steps, envs, rollout):
    log("=" * 70)
    log(f"🥊 STARTING PHASE 1: 1v1 BOXING ARENA (Target: {target_steps:,} steps)")
    log("=" * 70)
    cmd = [
        PYTHON, os.path.join(HERE, "rl", "train_arena.py"),
        "--steps", str(target_steps),
        "--envs", str(envs),
        "--rollout", str(rollout),
        "--export-every", "25",
        "--teacher-eps", "0.20",
        "--teacher-decay", "0.9995",
        "--resume"
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(HERE, "rl")
    proc = subprocess.Popen(cmd, env=env)
    return proc.wait()


def run_phase_city(target_steps, envs, rollout, init_ckpt):
    log("=" * 70)
    log(f"🏙️ STARTING PHASE 2: TORONTO CITY ENFORCER (Target: {target_steps:,} steps)")
    log(f"Initializing from: {init_ckpt}")
    log("=" * 70)
    cmd = [
        PYTHON, os.path.join(HERE, "rl", "train_fighter.py"),
        "--steps", str(target_steps),
        "--envs", str(envs),
        "--rollout", str(rollout),
        "--export-every", "25",
        "--teacher-eps", "0.35",
        "--teacher-decay", "0.9992",
        "--init-ckpt", init_ckpt,
        "--resume"
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(HERE, "rl")
    proc = subprocess.Popen(cmd, env=env)
    return proc.wait()


def main():
    args = parse_args()
    total_seconds = int(args.hours * 3600)
    arena_seconds = int(args.arena_hours * 3600)
    start_time = time.time()
    
    log(f"🚀 7-Hour Toronto Brawler Training Pipeline started.")
    log(f"Total budget: {args.hours:.1f} hours ({total_seconds:,} seconds).")
    log(f"Phase 1 (Arena): {args.arena_hours:.1f} hours. Phase 2 (City): {args.hours - args.arena_hours:.1f} hours.")
    
    # Estimate steps for ~6,000 FPS
    arena_target_steps = 25_000_000
    city_target_steps = 100_000_000
    
    # Phase 1: Hard 1v1 Arena
    rc = run_phase_arena(arena_target_steps, args.envs, args.rollout)
    if rc != 0:
        log(f"⚠️ Phase 1 exited with code {rc}. Proceeding to Phase 2.")
    
    # Snapshot Phase 1 weights
    arena_ckpt = os.path.join(HERE, "rl", "checkpoints", "fighter_arena_latest.pkl")
    snap_dir = os.path.join(HERE, "rl", "checkpoints", "snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    if os.path.exists(arena_ckpt):
        subprocess.run(["cp", arena_ckpt, os.path.join(snap_dir, "fighter_arena_phase1.pkl")])
        log(f"💾 Saved Phase 1 checkpoint snapshot.")
    
    # Phase 2: Toronto City Enforcer
    elapsed = time.time() - start_time
    remaining = total_seconds - elapsed
    log(f"Phase 1 complete in {elapsed/60:.1f} minutes. Remaining time: {remaining/3600:.2f} hours.")
    
    if remaining > 60:
        rc = run_phase_city(city_target_steps, args.envs, args.rollout, arena_ckpt)
        log(f"Phase 2 finished with code {rc}.")
    
    total_elapsed = time.time() - start_time
    log(f"🎉 7-Hour Training Pipeline finished in {total_elapsed/3600:.2f} hours!")


if __name__ == "__main__":
    main()
