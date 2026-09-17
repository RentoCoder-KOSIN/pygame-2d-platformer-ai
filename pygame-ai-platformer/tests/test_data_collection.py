"""README「10. Phase 4 — 機械学習」データ収集のスモークテスト。"""
import csv
import os
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from pygame_ai_platformer.collect_data import collect

EXPECTED_COLUMNS = {
    "time",
    "x",
    "y",
    "velocity_x",
    "velocity_y",
    "enemy_distance",
    "goal_distance",
    "hp",
    "action",
}


def test_collect_creates_one_csv_per_episode():
    with tempfile.TemporaryDirectory() as tmp:
        collect(episodes=2, agent_name="rule", max_steps=500, output_dir=tmp)
        files = [f for f in os.listdir(tmp) if f.endswith(".csv")]
        assert len(files) == 2


def test_csv_has_expected_columns_and_rows():
    with tempfile.TemporaryDirectory() as tmp:
        collect(episodes=1, agent_name="rule", max_steps=500, output_dir=tmp)
        files = [f for f in os.listdir(tmp) if f.endswith(".csv")]

        with open(os.path.join(tmp, files[0]), newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert set(reader.fieldnames) == EXPECTED_COLUMNS
        assert len(rows) > 0
        assert rows[0]["action"] in {"LEFT", "RIGHT", "JUMP", "NONE"}


def test_rule_agent_data_reaches_goal_state_in_filename():
    with tempfile.TemporaryDirectory() as tmp:
        collect(episodes=1, agent_name="rule", max_steps=3000, output_dir=tmp)
        files = os.listdir(tmp)
        assert any("CLEARED" in f for f in files)
