from dataset_adapters.bot_iot import BOTIoTAdapter
from features.engine import calculate_features
from detectors.engine import analyze_dataframe
import pandas as pd


DATASET_PATH = "data/sih_datasets/bot_iot"


print("=" * 70)
print("CYBER-ASTRA BoT-IoT EVALUATION")
print("=" * 70)


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

print("\n[1] LOADING DATASET...")

adapter = BOTIoTAdapter(DATASET_PATH)

df = adapter.load(
    nrows_per_file=5000
)

print(f"Rows loaded: {len(df)}")


# ------------------------------------------------------------
# 2. FEATURE ENGINEERING
# ------------------------------------------------------------

print("\n[2] FEATURE ENGINEERING...")

features = calculate_features(df)

print(f"Feature rows: {len(features)}")
print(f"Feature columns: {len(features.columns)}")


# ------------------------------------------------------------
# 3. RUN CYBER-ASTRA
# ------------------------------------------------------------

print("\n[3] RUNNING CYBER-ASTRA...")

alerts = analyze_dataframe(features)

print(f"Total alerts: {len(alerts)}")


# ------------------------------------------------------------
# 4. SHOW ALERT SUMMARY
# ------------------------------------------------------------

print("\n[4] CYBER-ASTRA ALERT SUMMARY")

if alerts.empty:

    print("No alerts generated.")

else:

    print(
        alerts[
            [
                "threat_class",
                "severity",
                "confidence",
                "src_ip",
                "dst_ip",
                "flow_id",
            ]
        ].to_string(index=False)
    )


# ------------------------------------------------------------
# 5. GROUND-TRUTH SUMMARY
# ------------------------------------------------------------

print("\n[5] GROUND TRUTH")

print(
    features["original_label"]
    .value_counts()
    .to_string()
)


# ------------------------------------------------------------
# 6. DETECTION COUNTS
# ------------------------------------------------------------

print("\n[6] DETECTION COUNTS")

if alerts.empty:

    print("No detections.")

else:

    print(
        alerts["threat_class"]
        .value_counts()
        .to_string()
    )


# ------------------------------------------------------------
# 7. MATCH ALERTS TO GROUND TRUTH
# ------------------------------------------------------------

print("\n[7] ALERT / GROUND-TRUTH ANALYSIS")

if not alerts.empty:

    ground_truth = (
        features[
            [
                "flow_id",
                "original_label",
                "original_subcategory",
            ]
        ]
        .drop_duplicates("flow_id")
    )

    evaluation = alerts.merge(
        ground_truth,
        on="flow_id",
        how="left",
    )

    print(
        evaluation[
            [
                "flow_id",
                "threat_class",
                "original_label",
                "original_subcategory",
                "confidence",
            ]
        ].to_string(index=False)
    )

else:

    evaluation = pd.DataFrame()


# ------------------------------------------------------------
# 8. SAVE RESULTS
# ------------------------------------------------------------

print("\n[8] SAVING RESULTS")

alerts.to_csv(
    "data/bot_iot_alerts.csv",
    index=False,
)

if not evaluation.empty:

    evaluation.to_csv(
        "data/bot_iot_alert_evaluation.csv",
        index=False,
    )

print("data/bot_iot_alerts.csv")

if not evaluation.empty:

    print("data/bot_iot_alert_evaluation.csv")


print("\n" + "=" * 70)
print("STATUS: BoT-IoT EVALUATION COMPLETE")
print("=" * 70)