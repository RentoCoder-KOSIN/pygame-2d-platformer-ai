"""README「8. Phase 2 — AIによる自動操作」のランダムAI。

後続のルールベースAI・機械学習AIと比較するためのベースラインになる。
"""
import random

from .agent import Agent
from ..game.state import Action


class RandomAgent(Agent):
    def predict(self, state):
        return random.choice(Action.values())
