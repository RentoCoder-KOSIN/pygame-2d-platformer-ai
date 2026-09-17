"""ステージ構成要素(足場・ゴール扉)とステージ構築処理。

README「4. ゲーム設計」でゲームとAIを分離する方針に従い、
ステージのレイアウトはこのファイルにまとめておく。
新しいステージを増やす場合は build_stage_2() のように追加していく。
"""
import pygame

from .enemy import Enemy

GROUND_COLOR = (139, 69, 19)
DOOR_COLOR = (255, 215, 0)
DOOR_WIDTH = 40
DOOR_HEIGHT = 60


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GROUND_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))


class Door(pygame.sprite.Sprite):
    """ゴール地点の扉"""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((DOOR_WIDTH, DOOR_HEIGHT))
        self.image.fill(DOOR_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))


def build_stage_1():
    """marioproto.py のステージ1(穴あり・扉ゴール)を構築する。

    Returns:
        platforms, enemies, door, stage_length
    """
    platforms = pygame.sprite.Group()
    ground1 = Platform(0, 350, 800, 50)
    ground2 = Platform(900, 350, 1100, 50)  # 800〜900pxは落とし穴
    block = Platform(400, 250, 150, 20)
    platforms.add(ground1, ground2, block)

    enemies = pygame.sprite.Group()
    enemies.add(Enemy(600, 320), Enemy(1300, 320))

    door = Door(1800, 290)

    stage_length = 2000
    return platforms, enemies, door, stage_length
