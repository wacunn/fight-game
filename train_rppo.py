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
    Callback that logs live progress to train_status.json and auto-exports
    weights to ai_model.json so the browser game can immediately test the latest checkpoint.
    """
    def __init__(self, export_freq=15000, status_file="train_status.json", verbose=1):
        super().__init__(verbose)
        self.export_freq = export_freq
        self.status_file = status_file
        self.start_time = time.time()
        self.last_export_step = 0
        self.recent_rewards = []

    def _on_step(self) -> bool:
        # Collect episode rewards
        for info in self.locals.get("infos", []):
            if "episode" in info:
                self.recent_rewards.append(info["episode"]["r"])
                if len(self.recent_rewards) > 50:
                    self.recent_rewards.pop(0)

        # Periodic status update & export
        if self.num_timesteps - self.last_export_step >= self.export_freq:
            self.last_export_step = self.num_timesteps
            elapsed = time.time() - self.start_time
            fps = self.num_timesteps / max(1.0, elapsed)
            mean_r = float(np.mean(self.recent_rewards)) if self.recent_rewards else 0.0

            status = {
                "step": self.num_timesteps,
                "elapsed_seconds": round(elapsed, 1),
                "fps": round(fps, 1),
                "mean_reward": round(mean_r, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
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
                    print(f"[{status['timestamp']}] Step {self.num_timesteps:,} | FPS: {fps:.1f} | Mean Reward: {mean_r:.2f} | Exported ai_model.json")
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

    progress_cb = LiveProgressAndExportCallback(export_freq=10000)

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
