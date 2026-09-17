"""README「11. Phase 5 — プレイヤー行動予測」の学習・推論のスモークテスト。"""
import os
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from pygame_ai_platformer.ai.ml_agent import MLAgent
from pygame_ai_platformer.collect_data import collect
from pygame_ai_platformer.game.game import Game
from pygame_ai_platformer.train_ml_agent import train


def test_train_and_predict_smoke():
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = os.path.join(tmp, "training")
        model_path = os.path.join(tmp, "model.joblib")

        # RuleAgentで少量のプレイデータを作り、それをそのまま学習データにする
        collect(episodes=15, agent_name="rule", max_steps=1000, output_dir=data_dir)
        model, acc = train(
            model_name="decision_tree",
            data_dir=data_dir,
            model_path=model_path,
            test_size=0.2,
        )

        assert os.path.exists(model_path)
        assert 0.0 <= acc <= 1.0

        agent = MLAgent(model_path=model_path)
        game = Game(render=False)
        state = game.reset()
        action = agent.predict(state)
        assert action in {"LEFT", "RIGHT", "JUMP", "NONE"}
        game.close()


def test_ml_agent_raises_clear_error_without_model():
    with tempfile.TemporaryDirectory() as tmp:
        missing_path = os.path.join(tmp, "does_not_exist.joblib")
        try:
            MLAgent(model_path=missing_path)
            assert False, "FileNotFoundErrorが発生するはず"
        except FileNotFoundError as e:
            assert "train-ml" in str(e)
