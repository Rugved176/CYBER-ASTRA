from dataset_adapters import CICIDS2017Adapter
from features.engine import calculate_features
from detectors.engine import analyze_dataframe

DATASET_ROOT = "data/sih_datasets/cic_ids2017"

print("=" * 70)
print("CYBER-ASTRA CIC-IDS2017 PIPELINE TEST")
print("=" * 70)

# --------------------------------------------------
# 1. LOAD DATASET
# --------------------------------------------------

adapter = CICIDS2017Adapter(DATASET_ROOT)

df = adapter.load(nrows_per_file=100)

print("\n[1] DATASET")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# --------------------------------------------------
# 2. ORIGINAL DATASET LABELS
# --------------------------------------------------

print("\n[2] ORIGINAL LABELS")
print(df["original_label"].value_counts())

# --------------------------------------------------
# 3. CYBER-ASTRA LABEL MAPPING
# --------------------------------------------------

print("\n[3] CYBER-ASTRA THREAT CLASSES")
print(df["threat_class"].value_counts())

# --------------------------------------------------
# 4. FEATURE ENGINEERING
# --------------------------------------------------

print("\n[4] FEATURE ENGINEERING")

features = calculate_features(df)

print("Feature rows:", len(features))
print("Feature columns:", len(features.columns))

# --------------------------------------------------
# 5. DETECTION ENGINE
# --------------------------------------------------

print("\n[5] DETECTION ENGINE")

detections = analyze_dataframe(features)

print("Detection rows:", len(detections))

print("\nDetection columns:")
print(list(detections.columns))

# --------------------------------------------------
# 6. SAMPLE RESULTS
# --------------------------------------------------

print("\n[6] SAMPLE DETECTION RESULTS")

print(
    detections.head(10).to_string(index=False)
)

# --------------------------------------------------
# COMPLETE
# --------------------------------------------------

print("\n" + "=" * 70)
print("CIC-IDS2017 → FEATURES → DETECTION")
print("STATUS: SUCCESS")
print("=" * 70)