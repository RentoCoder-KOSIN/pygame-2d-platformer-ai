"""README「11. Phase 5 — プレイヤー行動予測」で学習したモデルを使うAI。

train_ml_agent.py で学習・保存したモデル(models/player_action_model.joblib)を
読み込み、ゲーム状態から次の行動を予測する。
"""
import os

import joblib
import pandas as pd

from .agent import Agent

# <repo_root>/models/player_action_model.joblib
_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
)
DEFAULT_MODEL_PATH = os.path.join(_ROOT, "models", "player_action_model.joblib")

NO_ENEMY_DISTANCE = 9999  # train_ml_agent.py と同じ穴埋め値


class MLAgent(Agent):
    def __init__(self, model_path=DEFAULT_MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"{model_path} が見つかりません。先に `uv run train-ml` でモデルを学習してください。"
            )
        bundle = joblib.load(model_path)
        self.model = bundle["model"]
        self.features = bundle["features"]

    def predict(self, state):
        enemies = state["enemies"]
        enemy_distance = (
            min(abs(e["x"] - state["player_x"]) for e in enemies)
            if enemies
            else NO_ENEMY_DISTANCE
        )
        row = {
            "x": state["player_x"],
            "y": state["player_y"],
            "velocity_x": state["velocity_x"],
            "velocity_y": state["velocity_y"],
            "enemy_distance": enemy_distance,
            "goal_distance": state["goal_distance"],
            "hp": state["hp"],
        }
        features = pd.DataFrame([row], columns=self.features)
        return self.model.predict(features)[0]
