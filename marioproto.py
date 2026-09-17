import sys
import pygame

# --- 1. 初期設定と定数 ---
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("横スクロール＆クリア扉マリオ")
clock = pygame.time.Clock()

# 色の定義
SKY_BLUE = (107, 140, 255)
BROWN = (139, 69, 19)
RED = (230, 50, 50)
DARK_RED = (150, 30, 30)
YELLOW = (255, 215, 0)
WHITE = (255, 255, 255)

# --- 2. 各オブジェクトクラス ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.is_jumping = False

    def update(self, platforms):
        # 左右移動
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 4
        if keys[pygame.K_RIGHT]:
            self.rect.x += 4

        # ジャンプ
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.vel_y = -13
            self.is_jumping = True

        # 重力
        self.vel_y += 0.8
        self.rect.y += self.vel_y

        # 床との当たり判定
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0 and self.rect.bottom <= p.rect.bottom:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.is_jumping = False

class Goomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(DARK_RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = -2

    def update(self):
        self.rect.x += self.speed

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=(x, y))

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(YELLOW) # 金色の扉
        self.rect = self.image.get_rect(topleft=(x, y))

# 文字描画関数
def draw_text(text, size, x, y):
    font = pygame.font.SysFont("arial", size, bold=True)
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (x, y))

# --- 3. メイン処理 ---
def main():
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # プレイヤー作成
    player = Player(100, 200)
    all_sprites.add(player)

    # 横長のステージを作成（X軸: 0 〜 2000px）
    ground1 = Platform(0, 350, 800, 50)
    ground2 = Platform(900, 350, 1100, 50) # 800~900pxは穴（落とし穴）
    block = Platform(400, 250, 150, 20)
    platforms.add(ground1, ground2, block)
    all_sprites.add(ground1, ground2, block)

    # 敵の配置（奥にも配置）
    goomba1 = Goomba(600, 320)
    goomba2 = Goomba(1300, 320)
    enemies.add(goomba1, goomba2)
    all_sprites.add(goomba1, goomba2)

    # クリア用の扉をゴール地点（奥の1800px付近）に設置
    door = Door(1800, 290)
    all_sprites.add(door)

    # カメラのスクロールオフセット値
    camera_x = 0
    game_state = "PLAYING" # "PLAYING", "CLEARED", "GAMEOVER"

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_state == "PLAYING":
            # --- 更新処理 ---
            player.update(platforms)
            enemies.update()

            # カメラ追従：プレイヤーが画面中央（WIDTH/2）より右に行ったらカメラを動かす
            if player.rect.centerx - camera_x > WIDTH // 2:
                camera_x = player.rect.centerx - WIDTH // 2

            # 敵との当たり判定
            for enemy in pygame.sprite.spritecollide(player, enemies, False):
                if player.vel_y > 0 and player.rect.bottom <= enemy.rect.top + 15:
                    enemy.kill()
                    player.vel_y = -8
                else:
                    game_state = "GAMEOVER"

            # 扉（ゴール）との接触判定
            if player.rect.colliderect(door.rect):
                game_state = "CLEARED"

            # 穴に落ちた判定
            if player.rect.top > HEIGHT:
                game_state = "GAMEOVER"

        # --- 描画処理 ---
        screen.fill(SKY_BLUE)

        # カメラの位置オフセット（-camera_x）を適用して描画
        for sprite in all_sprites:
            screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

        # 状態メッセージの描画
        if game_state == "CLEARED":
            draw_text("STAGE CLEAR!", 60, WIDTH // 2 - 180, HEIGHT // 2 - 30)
        elif game_state == "GAMEOVER":
            draw_text("GAME OVER", 60, WIDTH // 2 - 150, HEIGHT // 2 - 30)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()