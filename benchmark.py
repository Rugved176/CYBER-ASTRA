import time
import json
import logging
from pathlib import Path
from collections import Counter

# ============================================================
# CYBER-ASTRA PROFESSIONAL BENCHMARK
# ============================================================

from ingestion.csv_ingest import load_flow_csv
from features.engine import calculate_features
from detectors.engine import analyze_dataframe


# ============================================================
# CONFIGURATION
# ============================================================

# Large synthetic benchmark dataset generated from the
# six-flow validation patterns.
DATA_FILE = "data/benchmark_flows.csv"

# Benchmark report generated for the Streamlit dashboard.
OUTPUT_FILE = Path("data/benchmark_report.json")

# Defined SIH benchmark target.
TARGET_THROUGHPUT_FPS = 100.0


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

logger = logging.getLogger("BENCHMARK")


# ============================================================
# BENCHMARK FUNCTION
# ============================================================

def run_benchmark():

    logger.info("=" * 60)
    logger.info("🚀 CYBER-ASTRA PERFORMANCE AUDIT")
    logger.info("=" * 60)

    logger.info(
        f"Benchmark Dataset : {DATA_FILE}"
    )

    logger.info(
        f"Target Throughput  : "
        f"{TARGET_THROUGHPUT_FPS:.2f} flows/sec"
    )

    metrics = {}

    try:

        # ====================================================
        # STAGE 1 — READ-ONLY INGESTION
        # ====================================================

        t0 = time.perf_counter()

        df = load_flow_csv(DATA_FILE)

        t1 = time.perf_counter()

        metrics["ingestion_time"] = t1 - t0

        logger.info(
            f"Stage 1: Ingestion complete in "
            f"{metrics['ingestion_time']:.4f}s"
        )

        # ====================================================
        # STAGE 2 — FEATURE ENGINEERING
        # ====================================================

        t2 = time.perf_counter()

        df_featured = calculate_features(df)

        t3 = time.perf_counter()

        metrics["engineering_time"] = t3 - t2

        logger.info(
            f"Stage 2: Feature Engineering complete in "
            f"{metrics['engineering_time']:.4f}s"
        )

        # ====================================================
        # STAGE 3 — THREAT DETECTION
        # ====================================================

        t4 = time.perf_counter()

        alerts = analyze_dataframe(df_featured)

        t5 = time.perf_counter()

        metrics["detection_time"] = t5 - t4

        logger.info(
            f"Stage 3: Threat Detection complete in "
            f"{metrics['detection_time']:.4f}s"
        )

        # ====================================================
        # FINAL METRICS
        # ====================================================

        total_time = (
            metrics["ingestion_time"]
            + metrics["engineering_time"]
            + metrics["detection_time"]
        )

        flow_count = len(df)

        alert_count = len(alerts)

        # ----------------------------------------------------
        # THROUGHPUT
        # ----------------------------------------------------

        throughput = (
            flow_count / total_time
            if total_time > 0
            else 0
        )

        # ----------------------------------------------------
        # AVERAGE PROCESSING COST
        # ----------------------------------------------------

        avg_processing_ms = (
            (total_time / flow_count) * 1000
            if flow_count > 0
            else 0
        )

        # ----------------------------------------------------
        # TARGET CHECK
        # ----------------------------------------------------

        target_achieved = (
            throughput >= TARGET_THROUGHPUT_FPS
        )

        # ====================================================
        # THREAT COVERAGE
        # ====================================================

        coverage = Counter(
            alert.get(
                "threat_class",
                "UNKNOWN"
            )
            for alert in alerts.to_dict(
                orient="records"
            )
        )

        # ====================================================
        # FINAL REPORT
        # ====================================================

        report = {

            "benchmark_type":
                "Offline synthetic replay",

            "dataset":
                DATA_FILE,

            "target_throughput_fps":
                TARGET_THROUGHPUT_FPS,

            "counts": {

                "flows_analyzed":
                    flow_count,

                "alerts_generated":
                    alert_count,
            },

            "stage_metrics_seconds": {

                "ingestion":
                    round(
                        metrics["ingestion_time"],
                        6
                    ),

                "engineering":
                    round(
                        metrics["engineering_time"],
                        6
                    ),

                "detection":
                    round(
                        metrics["detection_time"],
                        6
                    ),

                "total_execution":
                    round(
                        total_time,
                        6
                    ),
            },

            "performance_kpis": {

                "throughput_fps":
                    round(
                        throughput,
                        2
                    ),

                "avg_processing_ms_per_flow":
                    round(
                        avg_processing_ms,
                        3
                    ),

                "target_achieved":
                    target_achieved,
            },

            "threat_coverage":
                dict(coverage),
        }

        # ====================================================
        # SAVE REPORT
        # ====================================================

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=2
            )

        # ====================================================
        # CONSOLE SUMMARY
        # ====================================================

        print()
        print("─" * 60)
        print("🛡️  CYBER-ASTRA BENCHMARK RESULTS")
        print("─" * 60)

        print(
            f"Flows Analyzed      : "
            f"{flow_count}"
        )

        print(
            f"Alerts Generated    : "
            f"{alert_count}"
        )

        print(
            f"Execution Time      : "
            f"{total_time:.6f} sec"
        )

        print(
            f"Target Throughput   : "
            f"{TARGET_THROUGHPUT_FPS:.2f} flows/sec"
        )

        print(
            f"Measured Throughput : "
            f"{throughput:.2f} flows/sec"
        )

        print(
            f"Avg Processing Cost : "
            f"{avg_processing_ms:.3f} ms/flow"
        )

        print(
            f"Target Achieved     : "
            f"{'YES ✅' if target_achieved else 'NO ❌'}"
        )

        print("─" * 60)

        print("Threat Coverage:")

        for threat, count in coverage.items():

            print(
                f"  - {threat}: {count}"
            )

        print("─" * 60)

        print(
            f"Full report saved to: "
            f"{OUTPUT_FILE}"
        )

        print()

    except FileNotFoundError as error:

        logger.error(
            f"❌ BENCHMARK DATASET NOT FOUND: {error}"
        )

        logger.error(
            "Run generate_benchmark_data.py first."
        )

    except Exception as error:

        logger.error(
            f"💥 BENCHMARK FAILED: {error}"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_benchmark()