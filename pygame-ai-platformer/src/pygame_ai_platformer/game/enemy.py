"""敵キャラクター(ゴンバ風)。

README「3. ゲームの基本仕様」の「敵」要素に対応。
一定範囲を左右に往復するシンプルな挙動から始め、
将来的に種類を増やす場合はこのファイルにサブクラスを追加していく想定。
"""
import pygame

ENEMY_WIDTH = 30
ENEMY_HEIGHT = 30
ENEMY_COLOR = (150, 30, 30)
ENEMY_SPEED = 2
DEFAULT_PATROL_RANGE = 150


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_range=DEFAULT_PATROL_RANGE):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.start_pos = (x, y)
        self.left_bound = x - patrol_range
        self.right_bound = x + patrol_range
        self.speed = -ENEMY_SPEED

    def reset(self):
        self.rect.topleft = self.start_pos
        self.speed = -ENEMY_SPEED

    def update(self):
        self.rect.x += self.speed
        if self.rect.x <= self.left_bound or self.rect.x >= self.right_bound:
            self.speed *= -1
