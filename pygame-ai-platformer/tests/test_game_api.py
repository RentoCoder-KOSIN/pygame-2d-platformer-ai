"""README「5. AI用ゲームAPI」(reset / get_state / step)のスモークテスト。

SDL_VIDEODRIVER=dummy により、画面なし環境(CI等)でも実行できる。
`uv run pytest` を使えば、editable installされた pygame_ai_platformer を
そのままインポートできる(sys.path操作は不要)。
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from pygame_ai_platformer.game.game import Game
from pygame_ai_platformer.game.state import GameState


def test_reset_returns_initial_state():
    game = Game(render=False)
    state = game.reset()
    assert state["player_x"] == 100
    assert state["hp"] == 3
    assert state["goal_distance"] > 0
    game.close()


def test_step_returns_state_reward_done():
    game = Game(render=False)
    game.reset()
    state, reward, done = game.step("RIGHT")
    assert isinstance(state, dict)
    assert isinstance(reward, float)
    assert isinstance(done, bool)
    game.close()


def test_moving_right_moves_player_and_gives_reward():
    game = Game(render=False)
    game.reset()
    start_x = game.player.rect.x
    state, reward, _ = game.step("RIGHT")
    assert state["player_x"] > start_x
    assert reward > 0
    game.close()


def test_falling_into_pit_ends_game_over():
    game = Game(render=False)
    game.reset()
    # 落とし穴(800〜900px)の上まで強制移動させてゲームオーバーを誘発する
    game.player.rect.x = 850
    game.player.rect.y = 0

    done = False
    for _ in range(200):
        _, _, done = game.step("NONE")
        if done:
            break

    assert done
    assert game.state == GameState.GAMEOVER
    game.close()


def test_reaching_door_clears_stage():
    game = Game(render=False)
    game.reset()
    game.player.rect.x = game.door.rect.x
    game.player.rect.y = game.door.rect.y

    _, reward, done = game.step("NONE")

    assert done
    assert game.state == GameState.CLEARED
    assert reward >= 100
    game.close()
