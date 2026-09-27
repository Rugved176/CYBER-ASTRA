from pathlib import Path
import numpy as np
import pandas as pd


SOURCE_FILE = Path("data/sample_flows.csv")
OUTPUT_FILE = Path("data/ml_benign_training.csv")

SAMPLES_PER_FLOW = 500
RANDOM_SEED = 42


def generate_training_data():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Source file not found: {SOURCE_FILE}"
        )

    source = pd.read_csv(SOURCE_FILE)

    rng = np.random.default_rng(RANDOM_SEED)

    datasets = []

    numeric_columns = [
        "duration",
        "packets",
        "bytes_total",
    ]

    for _, base in source.iterrows():

        for _ in range(SAMPLES_PER_FLOW):

            row = base.copy()

            # Small natural variation around the benign baseline
            for column in numeric_columns:
                value = float(row[column])

                variation = rng.normal(
                    loc=1.0,
                    scale=0.08
                )

                row[column] = max(
                    0,
                    value * variation
                )

            # Keep ports/protocols realistic
            row["src_port"] = int(
                np.clip(
                    int(base["src_port"])
                    + rng.integers(-20, 21),
                    1024,
                    65535
                )
            )

            row["dst_port"] = int(base["dst_port"])

            datasets.append(row)

    training = pd.DataFrame(datasets)

    # Make integer network counters integers
    for column in ["packets", "bytes_total"]:
        training[column] = (
            training[column]
            .round()
            .astype(int)
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    training.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("=" * 60)
    print("CYBER-ASTRA ML TRAINING DATA")
    print("=" * 60)
    print(f"Source flows       : {len(source)}")
    print(f"Samples per flow   : {SAMPLES_PER_FLOW}")
    print(f"Generated samples  : {len(training)}")
    print(f"Output             : {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    generate_training_data()