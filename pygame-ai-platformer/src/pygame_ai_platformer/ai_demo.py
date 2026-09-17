"""README「8〜12. Phase2〜6」で作ったAIの動作確認用デモ。

指定したAI(rule/random/ml)にゲームを操作させ、画面で見えるようにする。
ゴール/ゲームオーバーになったら自動でreset()して繰り返す。
--smart-enemies を付けると、Phase6の「プレイヤーの行動を予測して逃げる敵」が有効になる
(事前に `uv run train-ml` でモデルを学習しておく必要がある)。

実行方法:
    uv run ai-demo                          # デフォルトはRuleAgent
    uv run ai-demo --agent random
    uv run ai-demo --agent ml                # 事前に `uv run train-ml` が必要
    uv run ai-demo --agent rule --smart-enemies   # Phase6の敵の反応を確認
"""
import argparse

import pygame

from .ai.random_agent import RandomAgent
from .ai.rule_agent import RuleAgent
from .game.game import Game

AGENTS = {
    "rule": RuleAgent,
    "random": RandomAgent,
}


def build_agent(name):
    if name == "ml":
        # MLAgentはmodels/にファイルがない環境ではimport時ではなく
        # 生成時にわかりやすいエラーを出したいので、ここで遅延import する
        from .ai.ml_agent import MLAgent

        return MLAgent()
    return AGENTS[name]()


def main():
    parser = argparse.ArgumentParser(description="AIにゲームをプレイさせるデモ")
    parser.add_argument("--agent", choices=["rule", "random", "ml"], default="rule")
    parser.add_argument(
        "--smart-enemies",
        action="store_true",
        help="Phase6: プレイヤーの行動予測モデルを使って敵に逃げ行動をさせる(要学習済みモデル)",
    )
    args = parser.parse_args()

    game = Game(render=True, smart_enemies=args.smart_enemies)
    agent = build_agent(args.agent)
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
