"""ゲーム本体。

README「5. AI用ゲームAPI」で定義されたインターフェースを実装する。

    game.reset()
    state = game.get_state()
    next_state, reward, done = game.step(action)

Game(render=True) で人間がキーボードで遊ぶことも、
Game(render=False) でAIが高速に大量プレイすることもできるようにしている
(README「14. Phase 8 — AIによる自動ゲームテスト」を見据えた設計)。
"""
import pygame

from .camera import Camera
from .player import Player
from .stage import build_stage_1
from .state import Action, GameState

WIDTH, HEIGHT = 800, 400
SKY_BLUE = (107, 140, 255)
WHITE = (255, 255, 255)

# README「16. 強化学習」の報酬設計を参考にした初期値
REWARD_GOAL = 100
REWARD_KILL_ENEMY = 10
REWARD_FORWARD = 1
REWARD_DAMAGE = -10
REWARD_DEATH = -100


class Game:
    def __init__(
        self,
        render=True,
        width=WIDTH,
        height=HEIGHT,
        smart_enemies=False,
        enemy_model_path=None,
    ):
        self.render_enabled = render
        self.width = width
        self.height = height

        pygame.init()
        if self.render_enabled:
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Pygame AI Platformer")
        else:
            # 画面を開かずに(オフスクリーンで)高速にstep()だけ回すためのSurface
            self.screen = pygame.Surface((self.width, self.height))

        self.clock = pygame.time.Clock()
        self.camera = Camera(self.width)

        # README「12. Phase 6 — プレイヤーを学習する敵」用。
        # Trueにすると、Phase5で学習したモデルでプレイヤーの次の行動を予測し、
        # 「JUMPしてきそう」な時に近くの敵を逃がす。要: 学習済みモデル(uv run train-ml)。
        self.smart_enemies = smart_enemies
        self.enemy_ai = None
        if self.smart_enemies:
            from ..ai.enemy_ai import PredictiveEnemyAI

            self.enemy_ai = PredictiveEnemyAI(model_path=enemy_model_path)

        self.player = None
        self.platforms = None
        self.enemies = None
        self.door = None
        self.stage_length = 0
        self.state = GameState.PLAYING
        self.finished = False
        self._prev_player_x = 0

        self.reset()

    # ------------------------------------------------------------------
    # README 5. AI用ゲームAPI
    # ------------------------------------------------------------------
    def reset(self):
        """ゲームを初期状態に戻す"""
        self.platforms, self.enemies, self.door, self.stage_length = build_stage_1()
        self.player = Player(100, 200)
        self.camera.reset()
        self.state = GameState.PLAYING
        self.finished = False
        self._prev_player_x = self.player.rect.x
        return self.get_state()

    def get_state(self):
        """現在のゲーム状態をdictで取得する(README 5.の例に準拠)"""
        enemies_info = [{"x": e.rect.x, "y": e.rect.y} for e in self.enemies]
        nearby_blocks = [
            {"x": p.rect.x, "y": p.rect.y, "width": p.rect.width, "height": p.rect.height}
            for p in self.platforms
            if abs(p.rect.centerx - self.player.rect.centerx) < self.width
        ]
        goal_distance = self.door.rect.x - self.player.rect.x

        return {
            "player_x": self.player.rect.x,
            "player_y": self.player.rect.y,
            "velocity_x": self.player.vel_x,
            "velocity_y": self.player.vel_y,
            "enemies": enemies_info,
            "nearby_blocks": nearby_blocks,
            "goal_distance": goal_distance,
            "hp": self.player.hp,
        }

    def step(self, action):
        """AIから1つの行動を受け取り、ゲームを1フレーム進める。

        Returns:
            next_state (dict), reward (float), done (bool)
        """
        if isinstance(action, Action):
            action = action.value

        reward = 0.0
        self._prev_player_x = self.player.rect.x

        if self.state == GameState.PLAYING:
            if self.smart_enemies and self.enemy_ai is not None:
                self._apply_smart_enemy_dodges()

            self.player.apply_action(action)
            self.player.update(self.platforms)
            self.enemies.update()
            self.camera.update(self.player.rect)

            reward += self._check_enemy_collisions()
            reward += self._check_goal_and_fall()
            # 前進した分だけ小さな報酬を与える(後退・停止には加算しない)
            reward += REWARD_FORWARD * max(0, self.player.rect.x - self._prev_player_x)

        done = self.state != GameState.PLAYING
        self.finished = done
        return self.get_state(), reward, done

    # ------------------------------------------------------------------
    # 内部処理
    # ------------------------------------------------------------------
    def _apply_smart_enemy_dodges(self):
        """README「12. Phase 6」用。プレイヤーの行動を予測し、近くの敵を逃がす。"""
        pre_state = self.get_state()
        dodges = self.enemy_ai.decide_dodges(pre_state)
        if not dodges:
            return
        for i, enemy in enumerate(self.enemies):
            if i in dodges:
                enemy.dodge(dodges[i])

    def _check_enemy_collisions(self):
        reward = 0.0
        for enemy in pygame.sprite.spritecollide(self.player, self.enemies, False):
            stomped = self.player.vel_y > 0 and self.player.rect.bottom <= enemy.rect.top + 15
            if stomped:
                enemy.kill()
                self.player.stomp_bounce()
                reward += REWARD_KILL_ENEMY
            elif self.player.take_damage():
                reward += REWARD_DAMAGE
                if self.player.hp <= 0:
                    self.state = GameState.GAMEOVER
                    reward += REWARD_DEATH
        return reward

    def _check_goal_and_fall(self):
        reward = 0.0
        if self.player.rect.colliderect(self.door.rect):
            self.state = GameState.CLEARED
            reward += REWARD_GOAL
        elif self.player.rect.top > self.height:
            self.state = GameState.GAMEOVER
            reward += REWARD_DEATH
        return reward

    # ------------------------------------------------------------------
    # 人間操作(キーボード)用のヘルパー
    # ------------------------------------------------------------------
    def action_from_keys(self):
        """現在押されているキーから行動を1つ決定する。

        Phase1は同時押し非対応(README 6.の初期行動セットに合わせる)。
        優先度: JUMP > LEFT > RIGHT
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.player.is_jumping:
            return Action.JUMP.value
        if keys[pygame.K_LEFT]:
            return Action.LEFT.value
        if keys[pygame.K_RIGHT]:
            return Action.RIGHT.value
        return Action.NONE.value

    # ------------------------------------------------------------------
    # 描画
    # ------------------------------------------------------------------
    def render(self):
        if not self.render_enabled:
            return

        self.screen.fill(SKY_BLUE)
        for sprite in [*self.platforms, *self.enemies, self.door, self.player]:
            self.screen.blit(sprite.image, self.camera.apply(sprite.rect))

        if self.state == GameState.CLEARED:
            self._draw_text("STAGE CLEAR!", 60, self.width // 2 - 180, self.height // 2 - 30)
        elif self.state == GameState.GAMEOVER:
            self._draw_text("GAME OVER", 60, self.width // 2 - 150, self.height // 2 - 30)
            self._draw_text("Rキーでリスタート", 20, self.width // 2 - 90, self.height // 2 + 40)
        else:
            self._draw_text(f"HP: {self.player.hp}", 24, 10, 10)

        pygame.display.flip()

    def _draw_text(self, text, size, x, y):
        font = pygame.font.SysFont("arial", size, bold=True)
        surface = font.render(text, True, WHITE)
        self.screen.blit(surface, (x, y))

    def tick(self, fps=60):
        self.clock.tick(fps)

    def close(self):
        pygame.quit()
