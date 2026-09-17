"""README「11. Phase 5 — プレイヤー行動予測」用の学習スクリプト。

data/training/ 以下のCSV(Phase4のcollect-dataで収集したプレイログ)を読み込み、
「ゲーム状態 → 次の行動」を予測する分類モデルを学習して models/ に保存する。

実行方法:
    uv run train-ml
    uv run train-ml --model random_forest
"""
import argparse
import glob
import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

FEATURE_COLUMNS = [
    "x",
    "y",
    "velocity_x",
    "velocity_y",
    "enemy_distance",
    "goal_distance",
    "hp",
]
LABEL_COLUMN = "action"

# 敵がいない(enemy_distance欠損)場合の穴埋め値。
# 「敵がとても遠い」のと同じ意味になるよう、大きめの定数にしておく。
NO_ENEMY_DISTANCE = 9999

# README「11. 最初に試すモデル」: Decision Tree / Random Forest
MODELS = {
    "decision_tree": lambda: DecisionTreeClassifier(max_depth=8, random_state=0),
    "random_forest": lambda: RandomForestClassifier(n_estimators=200, max_depth=10, random_state=0),
}

# <repo_root>/data/training/rule, <repo_root>/models
_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
# デフォルトはRuleAgent(良い手本)のデータのみを使う。
# RandomAgentのデータは状態と行動の相関が薄く、混ぜると精度が落ちる。
DEFAULT_DATA_DIR = os.path.join(_ROOT, "data", "training", "rule")
DEFAULT_MODEL_PATH = os.path.join(_ROOT, "models", "player_action_model.joblib")


def load_dataset(data_dir=DEFAULT_DATA_DIR):
    # data_dir直下・サブディレクトリ以下のどちらのCSVも拾えるようにしておく
    files = sorted(glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True))
    if not files:
        raise FileNotFoundError(
            f"{data_dir} にCSVが見つかりません。先に `uv run collect-data` でデータを集めてください。"
        )
    frames = [pd.read_csv(f) for f in files]
    df = pd.concat(frames, ignore_index=True)
    # 敵がいないフレームはenemy_distanceが空文字なので、大きな値で穴埋めする
    df["enemy_distance"] = pd.to_numeric(df["enemy_distance"], errors="coerce").fillna(NO_ENEMY_DISTANCE)
    return df, files


def train(model_name="decision_tree", data_dir=DEFAULT_DATA_DIR, model_path=DEFAULT_MODEL_PATH, test_size=0.2):
    df, files = load_dataset(data_dir)

    X = df[FEATURE_COLUMNS]
    y = df[LABEL_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=0, stratify=y
    )

    model = MODELS[model_name]()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump({"model": model, "features": FEATURE_COLUMNS}, model_path)

    print(f"学習に使用したCSV: {len(files)}件 / 行数: {len(df)}")
    print(f"テストデータ精度: {acc:.3f}")
    print(report)
    print(f"モデルを保存しました -> {model_path}")

    return model, acc


def main():
    parser = argparse.ArgumentParser(description="プレイヤー行動予測モデルの学習(README Phase5)")
    parser.add_argument("--model", choices=list(MODELS), default="decision_tree")
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    parser.add_argument("--model-path", default=DEFAULT_MODEL_PATH)
    parser.add_argument("--test-size", type=float, default=0.2)
    args = parser.parse_args()

    train(
        model_name=args.model,
        data_dir=args.data_dir,
        model_path=args.model_path,
        test_size=args.test_size,
    )


if __name__ == "__main__":
    main()
