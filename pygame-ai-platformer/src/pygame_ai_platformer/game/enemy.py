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
ENEMY_BOOST_SPEED = ENEMY_SPEED * 2  # Phase6: 迎撃時は通常の2倍速
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
        self._boost_timer = 0

    def reset(self):
        self.rect.topleft = self.start_pos
        self.speed = -ENEMY_SPEED
        self._boost_timer = 0

    def boost_toward(self, direction, duration=20):
        """Phase6用: directionへduration フレームだけ素早く動く(迎撃用の加速)。

        direction: +1(右へ)/-1(左へ)
        """
        self.speed = ENEMY_BOOST_SPEED * direction
        self._boost_timer = duration

    def update(self):
        if self._boost_timer > 0:
            self._boost_timer -= 1
            self.rect.x += self.speed
            if self._boost_timer == 0:
                # 加速が終わったら、その方向のまま通常速度のパトロールに戻す
                self.speed = ENEMY_SPEED if self.speed > 0 else -ENEMY_SPEED
            return

        self.rect.x += self.speed
        if self.rect.x <= self.left_bound or self.rect.x >= self.right_bound:
            self.speed *= -1
