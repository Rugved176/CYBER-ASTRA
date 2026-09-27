from pathlib import Path

import pandas as pd


SOURCE_FILE = Path("data/validation_flows.csv")
OUTPUT_FILE = Path("data/benchmark_flows.csv")

REPETITIONS = 1000


def generate_benchmark_dataset():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Source validation file not found: {SOURCE_FILE}"
        )

    source = pd.read_csv(SOURCE_FILE)

    datasets = []

    for repetition in range(REPETITIONS):

        batch = source.copy()

        batch["timestamp"] = (
            batch["timestamp"].astype(str)
            + f"-R{repetition:04d}"
        )

        datasets.append(batch)

    benchmark = pd.concat(
        datasets,
        ignore_index=True
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    benchmark.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("=" * 60)
    print("CYBER-ASTRA BENCHMARK DATASET")
    print("=" * 60)
    print(f"Source flows    : {len(source)}")
    print(f"Repetitions     : {REPETITIONS}")
    print(f"Generated flows : {len(benchmark)}")
    print(f"Output          : {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    generate_benchmark_dataset()