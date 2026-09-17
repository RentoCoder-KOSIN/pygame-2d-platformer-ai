"""README「8. Phase 2 — AIによる自動操作」の動作確認用デモ。

ランダムAIにゲームを操作させ、画面で見えるようにする。
ゴール/ゲームオーバーになったら自動でreset()して繰り返す。

実行方法:
    uv run ai-demo
または:
    uv run python -m pygame_ai_platformer.ai_demo
"""
import pygame

from .game.game import Game
from .ai.random_agent import RandomAgent


def main():
    game = Game(render=True)
    agent = RandomAgent()
    episode = 1

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        state = game.get_state()
        action = agent.predict(state)
        _, reward, done = game.step(action)
        game.render()
        game.tick(60)

        if done:
            print(f"[episode {episode}] result={game.state.value} reward={reward}")
            episode += 1
            game.reset()

    game.close()


if __name__ == "__main__":
    main()
