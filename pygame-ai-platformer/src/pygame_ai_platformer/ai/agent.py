"""AIエージェントの基底クラス。

README「9. Phase 3 — ルールベースAI」「10〜11. 機械学習」
「16. 強化学習」で登場する全てのエージェントは、
この Agent を継承して predict(state) を実装する想定。
"""
from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def predict(self, state):
        """game.get_state() のdictを受け取り、
        "LEFT" / "RIGHT" / "JUMP" / "NONE" のいずれかを返す。
        """
        raise NotImplementedError
