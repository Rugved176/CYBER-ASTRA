import joblib
import numpy as np
import pandas as pd

MODEL_PATH = "models/cyber_astra_anomaly.joblib"

FEATURE_COLUMNS = [
    "duration",
    "packets",
    "bytes_total",
    "packets_per_second",
    "bytes_per_second",
    "src_bytes",
    "dst_bytes",
    "src_entropy",
    "dst_host_count",
    "dst_port_count",
    "dns_query_length",
    "dns_entropy",
    "inter_arrival_mean",
    "inter_arrival_std",
    "byte_ratio",
    "flow_intensity",
]


def load_model():
    return joblib.load(MODEL_PATH)


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    defaults = {
        "src_entropy": 0.0,
        "dst_host_count": 1,
        "dst_port_count": 1,
        "dns_query_length": 0,
        "dns_entropy": 0.0,
        "inter_arrival_mean": 0.0,
        "inter_arrival_std": 0.0,
    }

    for column, value in defaults.items():
        if column not in result.columns:
            result[column] = value

    for column in FEATURE_COLUMNS:
        if column not in result.columns:
            result[column] = 0

    result = result[FEATURE_COLUMNS].copy()

    result = result.replace(
        [np.inf, -np.inf],
        np.nan
    )

    result = result.fillna(0)

    return result


def _normalize_scores(scores):
    """
    Convert Isolation Forest decision scores into
    an easy-to-read 0-1 anomaly score.

    Lower decision_function values indicate
    stronger anomaly behaviour.
    """

    scores = np.asarray(scores, dtype=float)

    # Logistic transformation.
    normalized = 1.0 / (
        1.0 + np.exp(scores * 8.0)
    )

    return np.clip(
        normalized,
        0.0,
        1.0
    )


def predict_anomaly(df: pd.DataFrame) -> pd.DataFrame:

    model = load_model()

    features = prepare_features(df)

    predictions = model.predict(features)

    raw_scores = model.decision_function(
        features
    )

    anomaly_scores = _normalize_scores(
        raw_scores
    )

    result = df.copy()

    result["ml_prediction"] = predictions

    result["ml_raw_score"] = raw_scores

    result["ml_anomaly_score"] = anomaly_scores

    result["ml_anomaly"] = (
        predictions == -1
    )

    return result