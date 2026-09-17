"""README「10. Phase 4 — 機械学習」用のデータ収集スクリプト。

指定エピソード数だけAI(デフォルトはRuleAgent)にプレイさせ、
1エピソードごとに data/training/ 以下へCSVとして保存する。

実行方法:
    uv run collect-data
    uv run collect-data --episodes 50 --agent random
    uv run collect-data --episodes 5 --render   # 画面を見ながら収集
"""
import argparse
import os

from .ai.random_agent import RandomAgent
from .ai.rule_agent import RuleAgent
from .game.game import Game
from .logger import EpisodeLogger

AGENTS = {
    "rule": RuleAgent,
    "random": RandomAgent,
}

# <repo_root>/data/training
DEFAULT_OUTPUT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "training")
)


def collect(episodes=20, agent_name="rule", max_steps=3000, output_dir=None, render=False):
    """episodes回プレイして、エピソードごとにCSVを1つ保存する。

    output_dir未指定の場合は data/training/<agent_name>/ に保存する
    (エージェントごとにデータを分けることで、質の異なるプレイを混ぜずに学習できる)。
    """
    if output_dir is None:
        output_dir = os.path.join(DEFAULT_OUTPUT_DIR, agent_name)

    agent = AGENTS[agent_name]()
    game = Game(render=render)
    logger = EpisodeLogger()

    os.makedirs(output_dir, exist_ok=True)
    summary = []

    for ep in range(1, episodes + 1):
        game.reset()
        logger.reset()

        for _ in range(max_steps):
            state = game.get_state()
            action = agent.predict(state)
            logger.log(state, action)
            _, _, done = game.step(action)

            if render:
                game.render()
                game.tick(60)
            if done:
                break

        result = game.state.value
        filename = f"episode_{ep:04d}_{agent_name}_{result}.csv"
        path = os.path.join(output_dir, filename)
        logger.save_csv(path)
        summary.append((ep, result, len(logger)))
        print(f"[episode {ep}] result={result} steps={len(logger)} -> {filename}")

    game.close()
    return summary


def main():
    parser = argparse.ArgumentParser(description="プレイデータ収集(README Phase4)")
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--agent", choices=list(AGENTS), default="rule")
    parser.add_argument("--max-steps", type=int, default=3000)
    parser.add_argument("--render", action="store_true", help="画面表示しながら収集する")
    args = parser.parse_args()

    collect(
        episodes=args.episodes,
        agent_name=args.agent,
        max_steps=args.max_steps,
        render=args.render,
    )


if __name__ == "__main__":
    main()
