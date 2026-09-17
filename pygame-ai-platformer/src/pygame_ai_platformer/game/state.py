"""ゲームの状態(State)と行動(Action)の定義。

README「6. AIの行動」に合わせて、Phase1では
LEFT / RIGHT / JUMP / NONE の4種類のみを扱う。
"""
from enum import Enum


class GameState(Enum):
    PLAYING = "PLAYING"
    CLEARED = "CLEARED"
    GAMEOVER = "GAMEOVER"


class Action(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    JUMP = "JUMP"
    NONE = "NONE"

    @classmethod
    def values(cls):
        """['LEFT', 'RIGHT', 'JUMP', 'NONE'] を返す(ランダムAI等で使用)"""
        return [a.value for a in cls]
