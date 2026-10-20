#!/usr/bin/env python3
"""
Overnight Training Script: Recurrent PPO (PPO with 128-unit recurrent core)
Trains on the Toronto brawl environment with multi-district spawning and goal conditioning.
Supports Apple Silicon M4 MPS acceleration and auto-exports to ai_model.json.
"""

import os
import sys
import time
import json
import argparse
import torch
import numpy as np

from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback, EvalCallback
from sb3_contrib import RecurrentPPO

from toronto_env import TorontoFightGymEnv
from export_weights import export_model_to_json

class LiveProgressAndExportCallback(BaseCallback):
    """
    Callback that logs live progress, loss values, reward curves, and district leaderboards
    to train_status.json and auto-exports weights to ai_model.json.
    """
    def __init__(self, export_freq=8000, status_file="train_status.json", target_steps=5_000_000, verbose=1):
        super().__init__(verbose)
        self.export_freq = export_freq
        self.status_file = status_file
        self.target_steps = target_steps
        self.start_time = time.time()
        self.last_export_step = 0
        self.recent_rewards = []
        self.history = []
        self.district_stats = {}

    def _on_step(self) -> bool:
        # Collect episode rewards and district performance
        for info in self.locals.get("infos", []):
            if "episode" in info:
                ep = info["episode"]
                r = float(ep.get("r", 0.0))
                self.recent_rewards.append(r)
                if len(self.recent_rewards) > 100:
                    self.recent_rewards.pop(0)

                dist = ep.get("district", "Downtown Grid Patrol")
                if dist not in self.district_stats:
                    self.district_stats[dist] = {"episodes": 0, "wins": 0, "total_r": 0.0}
                self.district_stats[dist]["episodes"] += 1
                self.district_stats[dist]["total_r"] += r
                if ep.get("won", False):
                    self.district_stats[dist]["wins"] += 1

        # Periodic status update & export
        if self.num_timesteps - self.last_export_step >= self.export_freq:
            self.last_export_step = self.num_timesteps
            elapsed = time.time() - self.start_time
            fps = self.num_timesteps / max(1.0, elapsed)
            mean_r = float(np.mean(self.recent_rewards)) if self.recent_rewards else 0.0

            # Pull loss metrics from SB3 logger if available
            vals = {}
            if hasattr(self.model, "logger") and hasattr(self.model.logger, "name_to_value"):
                vals = self.model.logger.name_to_value

            policy_loss = round(float(vals.get("train/policy_gradient_loss", 0.0)), 6)
            value_loss = round(float(vals.get("train/value_loss", 0.0)), 4)
            entropy_loss = round(float(vals.get("train/entropy_loss", 0.0)), 4)
            total_loss = round(float(vals.get("train/loss", 0.0)), 4)
            approx_kl = round(float(vals.get("train/approx_kl", 0.0)), 6)
            explained_var = round(float(vals.get("train/explained_variance", 0.0)), 4)

            # Build district leaderboard sorted by average score
            leaderboard = []
            for d_name, stat in self.district_stats.items():
                n_eps = stat["episodes"]
                avg_score = round(stat["total_r"] / max(1, n_eps), 2)
                win_pct = round((stat["wins"] / max(1, n_eps)) * 100.0, 1)
                status_label = "Mastered" if win_pct >= 75 else ("Combat Trained" if win_pct >= 40 else "Patrolling")
                leaderboard.append({
                    "district": d_name,
                    "episodes": n_eps,
                    "avg_reward": avg_score,
                    "win_rate": f"{win_pct}%",
                    "status": status_label
                })
            leaderboard.sort(key=lambda x: x["avg_reward"], reverse=True)
            for idx, entry in enumerate(leaderboard):
                entry["rank"] = idx + 1

            # Append to time-series history (keep up to 100 points)
            self.history.append({
                "step": self.num_timesteps,
                "reward": round(mean_r, 2),
                "policy_loss": policy_loss,
                "value_loss": value_loss,
                "entropy_loss": entropy_loss,
                "fps": round(fps, 1),
                "time": round(elapsed, 1),
            })
            if len(self.history) > 100:
                self.history.pop(0)

            # Compute ETA
            rem_steps = max(0, self.target_steps - self.num_timesteps)
            eta_seconds = rem_steps / max(1.0, fps)
            eta_hours = round(eta_seconds / 3600.0, 2)

            status = {
                "step": self.num_timesteps,
                "target_steps": self.target_steps,
                "progress_pct": round((self.num_timesteps / self.target_steps) * 100.0, 2),
                "elapsed_seconds": round(elapsed, 1),
                "fps": round(fps, 1),
                "eta_hours": eta_hours,
                "mean_reward": round(mean_r, 2),
                "best_reward": round(max([h["reward"] for h in self.history] or [mean_r]), 2),
                "policy_loss": policy_loss,
                "value_loss": value_loss,
                "entropy_loss": entropy_loss,
                "total_loss": total_loss,
                "approx_kl": approx_kl,
                "explained_variance": explained_var,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "leaderboard": leaderboard,
                "history": self.history
            }

            with open(self.status_file, "w") as f:
                json.dump(status, f, indent=2)

            # Save latest checkpoint & export json
            os.makedirs("checkpoints", exist_ok=True)
            ckpt_path = "checkpoints/rppo_toronto_latest.zip"
            self.model.save(ckpt_path)

            try:
                export_model_to_json(ckpt_path, "ai_model.json")
                if self.verbose:
                    print(f"[{status['timestamp']}] Step {self.num_timesteps:,} | FPS: {fps:.1f} | Mean Reward: {mean_r:.2f} | Pol Loss: {policy_loss} | Val Loss: {value_loss} | Exported ai_model.json")
            except Exception as e:
                print(f"Export warning: {e}")

        return True

def make_env():
    def _init():
        return TorontoFightGymEnv()
    return _init

def train(timesteps=5_000_000, device="auto", n_envs=4, lr=3e-4):
    print("=" * 70)
    print(" TORONTO BRAWL RL: RECURRENT PPO (128-UNIT RECURRENT CORE)")
    print("=" * 70)
    print(f"Target Timesteps: {timesteps:,}")
    print(f"Parallel Envs:    {n_envs}")
    print(f"Device:           {device}")
    print(f"Learning Rate:    {lr}")

    if device == "mps" and not torch.backends.mps.is_available():
        print("MPS not available, falling back to CPU")
        device = "cpu"

    # Multi-environment vectorization
    vec_env = DummyVecEnv([make_env() for _ in range(n_envs)])

    policy_kwargs = dict(
        lstm_hidden_size=128,
        n_lstm_layers=1,
        shared_lstm=False,
        enable_critic_lstm=True,
    )

    ckpt_latest = "checkpoints/rppo_toronto_latest.zip"
    if os.path.exists(ckpt_latest):
        print(f"Resuming training from checkpoint: {ckpt_latest}")
        model = RecurrentPPO.load(
            ckpt_latest,
            env=vec_env,
            device=device,
            tensorboard_log="logs/rppo_toronto"
        )
    else:
        model = RecurrentPPO(
            policy="MlpLstmPolicy",
            env=vec_env,
            learning_rate=lr,
            n_steps=512,
            batch_size=128,
            n_epochs=5,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,
            policy_kwargs=policy_kwargs,
            verbose=1,
            device=device,
            tensorboard_log="logs/rppo_toronto"
        )

    os.makedirs("checkpoints", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    progress_cb = LiveProgressAndExportCallback(export_freq=8000, target_steps=timesteps)

    print("\nStarting training loop...")
    try:
        model.learn(
            total_timesteps=timesteps,
            callback=progress_cb,
            progress_bar=False
        )
    except KeyboardInterrupt:
        print("\nTraining paused by user. Saving final checkpoint...")

    # Final save
    final_path = "checkpoints/rppo_toronto_final.zip"
    model.save(final_path)
    export_model_to_json(final_path, "ai_model.json")
    print(f"Final model saved to {final_path} and exported to ai_model.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timesteps", type=int, default=5_000_000, help="Total training steps")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu, mps, auto)")
    parser.add_argument("--n_envs", type=int, default=4, help="Number of parallel vectorized envs")
    args = parser.parse_args()

    train(timesteps=args.timesteps, device=args.device, n_envs=args.n_envs)
