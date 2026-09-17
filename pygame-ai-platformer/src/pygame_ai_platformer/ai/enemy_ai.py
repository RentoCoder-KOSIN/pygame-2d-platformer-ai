"""README「12. Phase 6 — プレイヤーを学習する敵」。

Phase5で学習した「プレイヤーの行動予測モデル」(MLAgentと同じモデル)を使い、
プレイヤーが次にJUMPしそう(=踏みつけを狙っていそう)だと予測できたら、
近くの敵をプレイヤーと反対方向へ逃がす。

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
プレイヤーに合わせた行動(踏まれる前に逃げる)
"""
from .ml_agent import MLAgent

DODGE_RANGE = 60           # このpx以内に敵がいる場合のみ「近い」とみなす
DODGE_DURATION_FRAMES = 20  # 逃げる動作を継続するフレーム数


class PredictiveEnemyAI:
    """プレイヤー行動予測モデルを使って、敵に「逃げる」指示を出す。"""

    def __init__(self, model_path=None):
        # MLAgentのモデル読み込み・特徴量抽出ロジックをそのまま再利用する
        self._ml_agent = MLAgent(model_path) if model_path else MLAgent()

    def predict_player_action(self, state):
        return self._ml_agent.predict(state)

    def decide_dodges(self, state):
        """各敵について、逃げるべきなら方向(+1/-1)を返す。

        Returns:
            {enemy_index: direction} の辞書。directionは
            +1(右へ逃げる)/-1(左へ逃げる)。逃げる必要がなければ空辞書。
        """
        predicted_action = self.predict_player_action(state)
        dodges = {}
        if predicted_action != "JUMP":
            return dodges

        player_x = state["player_x"]
        for i, enemy in enumerate(state["enemies"]):
            dx = enemy["x"] - player_x
            if abs(dx) <= DODGE_RANGE:
                # プレイヤーから見て敵がいる側(dx>=0なら右)へさらに逃げる
                dodges[i] = 1 if dx >= 0 else -1
        return dodges
