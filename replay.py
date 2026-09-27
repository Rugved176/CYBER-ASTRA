import time
from pathlib import Path

import pandas as pd

from ingestion.csv_ingest import load_flow_csv
from features.engine import calculate_features
from detectors.engine import analyze_dataframe


REPLAY_FILE = Path("data/validation_flows.csv")


def replay_flows(delay=1.0):
    if not REPLAY_FILE.exists():
        raise FileNotFoundError(
            f"Replay file not found: {REPLAY_FILE}"
        )

    df = load_flow_csv(REPLAY_FILE)

    for index, row in df.iterrows():

        processing_start = time.perf_counter()

        # Process exactly one flow at a time
        single_flow = pd.DataFrame([row])

        single_flow = calculate_features(
            single_flow
        )

        alerts = analyze_dataframe(
            single_flow
        )

        processing_time_ms = (
            time.perf_counter() - processing_start
        ) * 1000

        yield {
            "flow_number": index + 1,
            "flow_id": str(
                single_flow.iloc[0].get(
                    "flow_id",
                    "unknown"
                )
            ),
            "flow": row.to_dict(),
            "alerts": alerts.to_dict(
                orient="records"
            ),
            "processing_time_ms": round(
                processing_time_ms,
                3
            ),
        }

        if delay > 0:
            time.sleep(delay)