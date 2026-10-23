#!/usr/bin/env python3
"""
Nightly Self-Play Training Pipeline for Toronto Fight Game.

Executes iterative self-play training sessions (with minimal/decaying teacher guidance)
warm-started from existing checkpoints, then automatically refreshes the neural network
weights and re-bundles standalone play.html.

Usage:
  python3 train_nightly.py --mode fighter --steps 10000000
  python3 train_nightly.py --mode runner  --steps 10000000
  python3 train_nightly.py --mode both    --steps 5000000
"""
import argparse
import datetime
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable


def parse_args():
    ap = argparse.ArgumentParser(description="Toronto Fight Game Nightly Self-Play Trainer")
    ap.add_argument("--mode", choices=["arena", "fighter", "runner", "both"], default="arena",
                    help="Which neural network policy to train via self-play (default: arena)")
    ap.add_argument("--steps", type=int, default=10_000_000,
                    help="Total steps to train (default: 10,000,000)")
    ap.add_argument("--envs", type=int, default=128,
                    help="Number of vectorized parallel environments (default: 128)")
    ap.add_argument("--rollout", type=int, default=64,
                    help="Rollout steps per env before PPO update (default: 64)")
    ap.add_argument("--teacher-eps", type=float, default=0.05,
                    help="Initial fraction of teacher actions for self-play annealing (default: 0.05)")
    ap.add_argument("--teacher-decay", type=float, default=0.999,
                    help="Teacher decay factor per update (default: 0.999)")
    ap.add_argument("--lr", type=float, default=2e-4,
                    help="Learning rate (default: 2e-4)")
    return ap.parse_args()


def run_training(script_rel, steps, envs, rollout, teacher_eps, teacher_decay, lr, is_fighter=False, title=None):
    script_path = os.path.join(HERE, script_rel)
    label = title or ("🥊 STREET BRAWLER" if is_fighter else "📦 CRATE HUNTER")
    print("\n" + "=" * 70)
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Self-Play Training: {label}")
    print(f"Steps: {steps:,} | Envs: {envs} | Rollout: {rollout} | Teacher Eps: {teacher_eps}")
    print("=" * 70 + "\n")

    cmd = [
        PYTHON, script_path,
        "--steps", str(steps),
        "--envs", str(envs),
        "--rollout", str(rollout),
        "--teacher-eps", str(teacher_eps),
        "--teacher-decay", str(teacher_decay),
        "--lr", str(lr),
        "--resume",
    ]

    t0 = time.time()
    res = subprocess.run(cmd, cwd=HERE)
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"❌ Training failed with exit code {res.returncode}")
        return False

    print(f"✅ {label} completed {steps:,} steps in {elapsed / 60:.1f} minutes ({steps / max(elapsed, 1):.0f} sps)")
    return True


def rebundle():
    bundle_script = os.path.join(HERE, "tools", "bundle_play.py")
    print("\n📦 Updating standalone play.html with latest neural network weights...")
    res = subprocess.run([PYTHON, bundle_script], cwd=HERE)
    if res.returncode == 0:
        print("✅ play.html successfully bundled and updated!")
    else:
        print("⚠️ Warning: bundle_play.py returned code", res.returncode)


def main():
    args = parse_args()
    print("🌙 TORONTO FIGHT GAME - NIGHTLY SELF-PLAY TRAINER")
    print(f"Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {args.mode.upper()}")

    success = True
    if args.mode == "arena":
        ok = run_training("rl/train_arena.py", args.steps, args.envs, args.rollout,
                          args.teacher_eps, args.teacher_decay, args.lr, is_fighter=True, title="🥊 1v1 BOXING ARENA")
        success = success and ok

    if args.mode in ("fighter", "both"):
        fighter_steps = args.steps if args.mode == "fighter" else args.steps // 2
        ok = run_training("rl/train_fighter.py", fighter_steps, args.envs, args.rollout,
                          args.teacher_eps, args.teacher_decay, args.lr, is_fighter=True, title="🥊 STREET BRAWLER (CITY)")
        success = success and ok

    if args.mode in ("runner", "both"):
        runner_steps = args.steps if args.mode == "runner" else args.steps // 2
        ok = run_training("rl/train.py", runner_steps, args.envs, args.rollout,
                          args.teacher_eps, args.teacher_decay, args.lr, is_fighter=False, title="📦 CRATE HUNTER (CITY)")
        success = success and ok

    if success:
        rebundle()
        print("\n🎉 Nightly self-play cycle completed successfully!")
    else:
        print("\n❌ Completed with one or more errors.")


if __name__ == "__main__":
    main()
