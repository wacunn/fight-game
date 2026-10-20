#!/usr/bin/env python3
"""
Exports trained PyTorch RecurrentPPO policy weights to a compact ai_model.json
file so the game in JavaScript can run real-time inference at 60+ FPS with zero dependencies.
"""
import json
import os
import sys
import numpy as np
import torch

def export_model_to_json(model_zip_path, output_json_path="ai_model.json"):
    from sb3_contrib import RecurrentPPO
    from toronto_env import TorontoFightGymEnv

    print(f"Loading trained model from {model_zip_path}...")
    env = TorontoFightGymEnv()
    model = RecurrentPPO.load(model_zip_path, env=env, device="cpu")
    sd = model.policy.state_dict()

    # Extract LSTM actor weights
    w_ih = sd["lstm_actor.weight_ih_l0"].cpu().numpy().tolist()
    w_hh = sd["lstm_actor.weight_hh_l0"].cpu().numpy().tolist()
    b_ih = sd["lstm_actor.bias_ih_l0"].cpu().numpy()
    b_hh = sd["lstm_actor.bias_hh_l0"].cpu().numpy()
    b_lstm = (b_ih + b_hh).tolist()

    # Extract MLP policy layers
    w_p0 = sd["mlp_extractor.policy_net.0.weight"].cpu().numpy().tolist()
    b_p0 = sd["mlp_extractor.policy_net.0.bias"].cpu().numpy().tolist()
    w_p2 = sd["mlp_extractor.policy_net.2.weight"].cpu().numpy().tolist()
    b_p2 = sd["mlp_extractor.policy_net.2.bias"].cpu().numpy().tolist()

    # Extract Action head
    w_act = sd["action_net.weight"].cpu().numpy().tolist()
    b_act = sd["action_net.bias"].cpu().numpy().tolist()

    export_dict = {
        "version": "1.0",
        "arch": "RecurrentPPO_LSTM128_MLP64",
        "obs_dim": 56,
        "lstm_hidden_dim": 128,
        "mlp_dim": 64,
        "action_dim": 15, # [0..8] Move, [9..14] Action
        "weights": {
            "lstm_w_ih": w_ih,
            "lstm_w_hh": w_hh,
            "lstm_bias": b_lstm,
            "p0_w": w_p0,
            "p0_b": b_p0,
            "p2_w": w_p2,
            "p2_b": b_p2,
            "act_w": w_act,
            "act_b": b_act,
        }
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(export_dict, f)

    sz_kb = os.path.getsize(output_json_path) / 1024.0
    print(f"Successfully exported policy to {output_json_path} ({sz_kb:.1f} KB)")
    return output_json_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        zip_path = sys.argv[1]
    else:
        zip_path = "checkpoints/best_model.zip"
        if not os.path.exists(zip_path):
            zip_path = "checkpoints/rppo_toronto_latest.zip"
    export_model_to_json(zip_path, "ai_model.json")
