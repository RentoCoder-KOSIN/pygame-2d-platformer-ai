"""README「9. Phase 3 — ルールベースAI」。

人間が決めた単純なルールでゴールを目指すAI。Random Agentとの比較用ベースライン。

ルール(優先度順):
    1. 少し先に穴がある → ジャンプ
    2. 少し先に敵がいる → ジャンプ(踏みつけを狙う)
    3. それ以外          → 右へ進む(ゴールは常に右側にあるため)
"""

from ..game.state import Action
from .agent import Agent

HOLE_LOOKAHEAD = 40  # このpx先に足場がなければ「穴が近い」と判断する
ENEMY_JUMP_RANGE = 50  # このpx以内前方に敵がいたら「敵が近い」と判断する
PLAYER_HEIGHT = 40


class RuleAgent(Agent):
    def predict(self, state):
        player_x = state["player_x"]
        player_bottom = state["player_y"] + PLAYER_HEIGHT

        if self._enemy_is_near(state, player_x):
            return Action.JUMP.value

        if self._hole_is_ahead(state, player_x, player_bottom):
            return Action.JUMP.value

        return Action.RIGHT.value

    def _enemy_is_near(self, state, player_x):
        for enemy in state["enemies"]:
            dx = enemy["x"] - player_x
            if 0 < dx <= ENEMY_JUMP_RANGE:
                return True
        return False

    def _hole_is_ahead(self, state, player_x, player_bottom):
        check_x = player_x + HOLE_LOOKAHEAD
        for block in state["nearby_blocks"]:
            covers_x = block["x"] <= check_x <= block["x"] + block["width"]
            is_ground_level = block["y"] >= player_bottom - 10
            if covers_x and is_ground_level:
                return False
        return True
