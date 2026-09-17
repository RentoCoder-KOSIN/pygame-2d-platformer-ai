"""README「10. Phase 4 — 機械学習」用のプレイログ記録。

1エピソード分の (座標・速度・最寄りの敵との距離・ゴールまでの距離・HP・行動) を
フレーム単位で溜めておき、CSVとして書き出す。Phase5の行動予測モデルの
学習データとして使うことを想定している。
"""
import csv
import os
import time as time_module


class EpisodeLogger:
    """1エピソード分のプレイログを溜めて、CSVへ書き出す。"""

    FIELDNAMES = [
        "time",
        "x",
        "y",
        "velocity_x",
        "velocity_y",
        "enemy_distance",
        "goal_distance",
        "hp",
        "action",
    ]

    def __init__(self):
        self._rows = []
        self._start_time = None

    def reset(self):
        """新しいエピソードの記録を開始する"""
        self._rows = []
        self._start_time = time_module.perf_counter()

    def log(self, state, action):
        """1フレーム分の記録を追加する。

        state: game.get_state() の戻り値
        action: そのフレームで実行した行動 ("LEFT"/"RIGHT"/"JUMP"/"NONE")
        """
        if self._start_time is None:
            self.reset()

        self._rows.append(
            {
                "time": round(time_module.perf_counter() - self._start_time, 4),
                "x": state["player_x"],
                "y": state["player_y"],
                "velocity_x": state["velocity_x"],
                "velocity_y": state["velocity_y"],
                "enemy_distance": self._nearest_enemy_distance(state),
                "goal_distance": state["goal_distance"],
                "hp": state["hp"],
                "action": action,
            }
        )

    def _nearest_enemy_distance(self, state):
        enemies = state["enemies"]
        if not enemies:
            return ""
        return min(abs(e["x"] - state["player_x"]) for e in enemies)

    def save_csv(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            writer.writerows(self._rows)

    def __len__(self):
        return len(self._rows)
