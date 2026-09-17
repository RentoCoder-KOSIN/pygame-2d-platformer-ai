"""プレイヤークラス。

キーボード入力もAIの行動もいったん apply_action() に集約することで、
人間操作とAI操作(game.step())の両方から同じ物理演算を使えるようにしている。
"""
import pygame

PLAYER_WIDTH = 30
PLAYER_HEIGHT = 40
PLAYER_COLOR = (230, 50, 50)

MOVE_SPEED = 4
JUMP_POWER = -13
GRAVITY = 0.8

MAX_HP = 3
INVINCIBLE_FRAMES = 60  # 被弾後の無敵時間(フレーム数)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.start_pos = (x, y)
        self.vel_x = 0
        self.vel_y = 0
        self.is_jumping = False
        self.hp = MAX_HP
        self.invincible_timer = 0

    def reset(self):
        self.rect.topleft = self.start_pos
        self.vel_x = 0
        self.vel_y = 0
        self.is_jumping = False
        self.hp = MAX_HP
        self.invincible_timer = 0

    def apply_action(self, action):
        """行動(文字列)を受け取り、速度に反映する。

        action: "LEFT" / "RIGHT" / "JUMP" / "NONE"
        Phase1では同時押しを扱わないシンプルな1行動のみ対応。
        ただしJUMPは横方向の速度を維持する(直前のRIGHT/LEFTの慣性を殺さない)。
        そうしないと「ジャンプする度に足踏みして前進が止まる」動きになってしまう。
        """
        if action == "LEFT":
            self.vel_x = -MOVE_SPEED
        elif action == "RIGHT":
            self.vel_x = MOVE_SPEED
        elif action == "NONE":
            self.vel_x = 0
        elif action == "JUMP":
            if not self.is_jumping:
                self.vel_y = JUMP_POWER
                self.is_jumping = True
            # vel_xは変更しない(直前の移動方向の慣性を維持)

    def update(self, platforms):
        prev_bottom = self.rect.bottom

        # 横移動
        self.rect.x += self.vel_x

        # 重力
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # 接地判定: 落下中に、直前フレームでは足場より上にいた場合のみ着地させる
        self.is_jumping = True
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y >= 0 and prev_bottom <= p.rect.top + 1:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.is_jumping = False

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def take_damage(self):
        """被弾処理。無敵時間中はダメージを無視してFalseを返す。"""
        if self.invincible_timer > 0:
            return False
        self.hp -= 1
        self.invincible_timer = INVINCIBLE_FRAMES
        return True

    def stomp_bounce(self):
        """敵を踏んだ時の小ジャンプ"""
        self.vel_y = -8
