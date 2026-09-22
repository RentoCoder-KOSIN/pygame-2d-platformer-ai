"""README「12. Phase 6 — プレイヤーを学習する敵」。

Phase5で学習した「プレイヤーの行動予測モデル」(MLAgentと同じモデル)を使い、
プレイヤーが次にJUMPしそう(=踏みつけを狙っていそう)だと予測できたら、
近くの敵がプレイヤーの着地予測地点へ先回りして待ち構える(迎撃)。

ただ逃げるだけだと「敵に近づけば勝手に道が開く」だけの単調な挙動になるため、
README原文の「敵がジャンプ先を予測 → 迎撃」通り、着地点を奪いに行く方に変更している。

プレイヤー
    ↓
行動データ
    ↓
機械学習(Phase5のモデルを再利用)
    ↓
プレイヤーの行動予測
    ↓
敵AI(このファイル)
    ↓
プレイヤーに合わせた行動(着地点で待ち構える)
"""

from .ml_agent import MLAgent

INTERCEPT_RANGE = 150  # このpx以内に敵がいる場合のみ迎撃対象にする
INTERCEPT_LOOKAHEAD_FRAMES = 25  # 現在の横速度から何フレーム先の着地点を狙うか
INTERCEPT_DURATION_FRAMES = 20  # 迎撃のため加速する時間(フレーム数)


class PredictiveEnemyAI:
    """プレイヤー行動予測モデルを使って、敵に「迎撃」指示を出す。"""

    def __init__(self, model_path=None):
        # MLAgentのモデル読み込み・特徴量抽出ロジックをそのまま再利用する
        self._ml_agent = MLAgent(model_path) if model_path else MLAgent()

    def predict_player_action(self, state):
        return self._ml_agent.predict(state)

    def decide_intercepts(self, state):
        """各敵について、迎撃に動くべきなら方向(+1/-1)を返す。

        「プレイヤーがJUMPしそう」と予測できた時だけ、
        現在の横速度から着地予測地点を計算し、
        近くの敵をそこへ向けて動かす(逃げるのではなく先回りする)。

        Returns:
            {enemy_index: direction} の辞書。directionは
            +1(右へ)/-1(左へ)。迎撃不要なら空辞書。
        """
        predicted_action = self.predict_player_action(state)
        intercepts = {}
        if predicted_action != "JUMP":
            return intercepts

        player_x = state["player_x"]
        landing_x = player_x + state["velocity_x"] * INTERCEPT_LOOKAHEAD_FRAMES

        for i, enemy in enumerate(state["enemies"]):
            dx = enemy["x"] - player_x
            if abs(dx) <= INTERCEPT_RANGE:
                # 敵の現在地から見て、着地予測地点がどちら側かへ動く
                intercepts[i] = 1 if landing_x >= enemy["x"] else -1
        return intercepts
