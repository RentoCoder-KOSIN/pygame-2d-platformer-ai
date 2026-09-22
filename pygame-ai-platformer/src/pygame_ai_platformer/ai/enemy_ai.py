"""README「12. Phase 6 — プレイヤーを学習する敵」。

Phase5で学習した「プレイヤーの行動予測モデル」(MLAgentと同じモデル)を使い、
プレイヤーが次にJUMPしそう(=踏みつけを狙っていそう)だと予測できたら、
近くの敵がプレイヤーへ向かって突っ込む(迎撃)。

最初は「プレイヤーの着地予測地点(25フレーム先)」を狙う実装にしていたが、
プレイヤーの進行方向側にいる敵は、着地予測地点が自分の位置より
さらに先(プレイヤーと同じ方向)になりやすく、結果的に
「敵がプレイヤーと同じ方向・同じ速度で走り、距離を保ったまま
逃げ続けているように見える」という問題があった。
そのため、素直に「プレイヤーの現在位置へ向かって突っ込む」方式に変更している。
これなら敵とプレイヤーは常に近づき合う(衝突コースに入る)ため、
「気づいたら敵が迫ってくる」という緊張感のある迎撃になる。

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
プレイヤーに合わせた行動(気配を察知して突っ込む)
"""

from .ml_agent import MLAgent

INTERCEPT_RANGE = 150  # このpx以内に敵がいる場合のみ迎撃対象にする
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
        近くの敵をプレイヤーの現在位置へ向けて突っ込ませる。

        Returns:
            {enemy_index: direction} の辞書。directionは
            +1(右へ)/-1(左へ)。迎撃不要なら空辞書。
        """
        predicted_action = self.predict_player_action(state)
        intercepts = {}
        if predicted_action != "JUMP":
            return intercepts

        player_x = state["player_x"]
        for i, enemy in enumerate(state["enemies"]):
            dx = enemy["x"] - player_x
            if dx == 0 or abs(dx) > INTERCEPT_RANGE:
                continue
            # 敵からプレイヤーへ向かう方向(dx>0なら敵は右側にいるので左へ、の逆)
            intercepts[i] = -1 if dx > 0 else 1
        return intercepts
