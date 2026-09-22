"""README「12. Phase 6 — プレイヤーを学習する敵」のスモークテスト。"""

import os
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from pygame_ai_platformer.ai.enemy_ai import PredictiveEnemyAI
from pygame_ai_platformer.collect_data import collect
from pygame_ai_platformer.game.game import Game
from pygame_ai_platformer.train_ml_agent import train


def _train_tiny_model(tmp_dir):
    data_dir = os.path.join(tmp_dir, "training")
    model_path = os.path.join(tmp_dir, "model.joblib")
    collect(episodes=15, agent_name="rule", max_steps=1000, output_dir=data_dir)
    train(
        model_name="decision_tree",
        data_dir=data_dir,
        model_path=model_path,
        test_size=0.2,
    )
    return model_path


def test_predictive_enemy_ai_predicts_valid_action():
    with tempfile.TemporaryDirectory() as tmp:
        model_path = _train_tiny_model(tmp)
        enemy_ai = PredictiveEnemyAI(model_path=model_path)

        game = Game(render=False)
        state = game.reset()
        action = enemy_ai.predict_player_action(state)
        assert action in {"LEFT", "RIGHT", "JUMP", "NONE"}
        game.close()


def test_decide_intercepts_only_targets_nearby_enemies_on_jump():
    with tempfile.TemporaryDirectory() as tmp:
        model_path = _train_tiny_model(tmp)
        enemy_ai = PredictiveEnemyAI(model_path=model_path)

        state = {
            "player_x": 500,
            "player_y": 300,
            "velocity_x": 4,
            "velocity_y": 0,
            "enemies": [
                {"x": 520, "y": 320},  # 近い(迎撃対象になりうる)
                {"x": 900, "y": 320},  # 遠い(対象外)
            ],
            "nearby_blocks": [],
            "goal_distance": 800,
            "hp": 3,
        }

        intercepts = enemy_ai.decide_intercepts(state)
        # 遠い敵(index=1)は対象にならない
        assert 1 not in intercepts
        for direction in intercepts.values():
            assert direction in (1, -1)


def test_intercept_aims_at_predicted_landing_spot():
    """プレイヤーが右へ進行中なら、着地予測地点も右側になり、
    敵から見てその方向(+1)へ迎撃するはず。"""
    with tempfile.TemporaryDirectory() as tmp:
        model_path = _train_tiny_model(tmp)
        enemy_ai = PredictiveEnemyAI(model_path=model_path)

        state = {
            "player_x": 500,
            "player_y": 300,
            "velocity_x": 4,  # 右へ進行中
            "velocity_y": 0,
            "enemies": [{"x": 500, "y": 320}],  # プレイヤーと同じx
            "nearby_blocks": [],
            "goal_distance": 800,
            "hp": 3,
        }

        intercepts = enemy_ai.decide_intercepts(state)
        if intercepts:
            assert intercepts[0] == 1


def test_game_with_smart_enemies_runs_without_crashing():
    with tempfile.TemporaryDirectory() as tmp:
        model_path = _train_tiny_model(tmp)

        from pygame_ai_platformer.ai.rule_agent import RuleAgent

        game = Game(render=False, smart_enemies=True, enemy_model_path=model_path)
        agent = RuleAgent()

        game.reset()
        for _ in range(500):
            state = game.get_state()
            action = agent.predict(state)
            _, _, done = game.step(action)
            if done:
                break

        game.close()
