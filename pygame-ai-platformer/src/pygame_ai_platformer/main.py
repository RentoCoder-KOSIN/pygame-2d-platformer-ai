"""README「7. Phase 1 — ゲーム制作」用のエントリーポイント。

キーボードで普通に遊べる状態にする(まだAIは使わない)。

実行方法:
    uv run play
または:
    uv run python -m pygame_ai_platformer.main
"""
import pygame

from .game.game import Game


def main():
    game = Game(render=True)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                game.reset()

        action = game.action_from_keys()
        game.step(action)
        game.render()
        game.tick(60)

    game.close()


if __name__ == "__main__":
    main()
