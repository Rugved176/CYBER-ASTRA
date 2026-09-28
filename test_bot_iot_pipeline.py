from dataset_adapters import BOTIoTAdapter
from features.engine import calculate_features
from detectors.engine import analyze_dataframe

DATASET_ROOT = "data/sih_datasets/bot_iot"

print("=" * 70)
print("CYBER-ASTRA BoT-IoT PIPELINE TEST")
print("=" * 70)

# --------------------------------------------------
# 1. LOAD DATASET
# --------------------------------------------------

print("\n[1] LOADING BoT-IoT...")

adapter = BOTIoTAdapter(DATASET_ROOT)

df = adapter.load(
    nrows_per_file=100
)

print("Rows loaded:", len(df))
print("Columns:", len(df.columns))


# --------------------------------------------------
# 2. FEATURE ENGINEERING
# --------------------------------------------------

print("\n[2] FEATURE ENGINEERING...")

features = calculate_features(df)

print("Feature rows:", len(features))
print("Feature columns:", len(features.columns))


# --------------------------------------------------
# 3. SHOW IMPORTANT FEATURES
# --------------------------------------------------

print("\n[3] FEATURE SAMPLE")

important_features = [
    "flow_id",
    "protocol",
    "dst_port",
    "inter_arrival_mean",
    "inter_arrival_std",
]

available_features = [
    col for col in important_features
    if col in features.columns
]

print(
    features[available_features]
    .head(10)
    .to_string(index=False)
)


# --------------------------------------------------
# 4. DETECTION PIPELINE
# --------------------------------------------------

print("\n[4] RUNNING CYBER-ASTRA DETECTION...")

alerts = analyze_dataframe(features)

print("Detection rows:", len(alerts))


# --------------------------------------------------
# 5. DETECTION SUMMARY
# --------------------------------------------------

print("\n[5] DETECTION SUMMARY")

if len(alerts) > 0:

    print(
        alerts["threat_class"]
        .value_counts()
        .to_string()
    )

else:

    print("No alerts generated.")


# --------------------------------------------------
# 6. DATASET LABEL vs DETECTION
# --------------------------------------------------

print("\n[6] ORIGINAL DATASET LABELS")

print(
    df["threat_class"]
    .value_counts()
    .to_string()
)


# --------------------------------------------------
# 7. SAMPLE ALERTS
# --------------------------------------------------

if len(alerts) > 0:

    print("\n[7] SAMPLE ALERTS")

    alert_columns = [
        "threat_class",
        "severity",
        "confidence",
        "src_ip",
        "dst_ip",
        "evidence",
    ]

    available_alert_columns = [
        col for col in alert_columns
        if col in alerts.columns
    ]

    print(
        alerts[available_alert_columns]
        .head(10)
        .to_string(index=False)
    )


# --------------------------------------------------
# COMPLETE
# --------------------------------------------------

print("\n" + "=" * 70)
print("STATUS: BoT-IoT PIPELINE TEST COMPLETE")
print("=" * 70)