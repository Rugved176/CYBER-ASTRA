from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from features.engine import calculate_features
from ai.ml_detector import FEATURE_COLUMNS


DATA_FILE = Path("data/ml_benign_training.csv")
MODEL_FILE = Path("models/cyber_astra_anomaly.joblib")


def train_model():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Training data not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    # Apply CYBER-ASTRA feature engineering
    df = calculate_features(df)

    # The basic sample dataset does not contain every
    # advanced network feature yet.
    # Add unavailable features as neutral defaults.
    default_features = {
        "src_entropy": 0.0,
        "dst_host_count": 1,
        "dst_port_count": 1,
        "dns_query_length": 0,
        "dns_entropy": 0.0,
        "inter_arrival_mean": 0.0,
        "inter_arrival_std": 0.0,
    }

    for column, default_value in default_features.items():
        if column not in df.columns:
            df[column] = default_value

    # Make sure every expected ML feature exists
    for column in FEATURE_COLUMNS:
        if column not in df.columns:
            df[column] = 0

    X = df[FEATURE_COLUMNS].copy()

    X = X.replace(
        [float("inf"), float("-inf")],
        0
    )

    X = X.fillna(0)

    print("=" * 60)
    print("CYBER-ASTRA ML MODEL TRAINING")
    print("=" * 60)

    print(f"Training samples : {len(X)}")
    print(f"Features         : {len(FEATURE_COLUMNS)}")

    model = IsolationForest(
        n_estimators=150,
        contamination="auto",
        random_state=42,
        n_jobs=-1
    )

    model.fit(X)

    MODEL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    print()
    print("MODEL TRAINING COMPLETE")
    print(f"Model saved      : {MODEL_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    train_model()