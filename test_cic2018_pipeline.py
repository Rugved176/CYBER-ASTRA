from dataset_adapters import CICIDS2018Adapter
from features.engine import calculate_features
from detectors.engine import analyze_dataframe


DATASET_ROOT = "data/sih_datasets/cic_ids2018"

print("=" * 70)
print("CYBER-ASTRA CIC-IDS2018 PIPELINE TEST")
print("=" * 70)

adapter = CICIDS2018Adapter(DATASET_ROOT)

df = adapter.load(nrows_per_file=100)

print("\n[1] DATASET")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n[2] ORIGINAL LABELS")
print(df["original_label"].value_counts())

print("\n[3] CYBER-ASTRA MAPPING")
print(df["threat_class"].value_counts())

print("\n[4] FEATURE ENGINEERING")

features = calculate_features(df)

print("Feature rows:", len(features))
print("Feature columns:", len(features.columns))

print("\n[5] DETECTION ENGINE")

detections = analyze_dataframe(features)

print("Detection rows:", len(detections))

print("\n[6] DETECTIONS")
print(detections["threat_class"].value_counts())

print("\n[7] SAMPLE RESULTS")
print(detections.head(10).to_string(index=False))

print("\n" + "=" * 70)
print("CIC-IDS2018 → FEATURES → DETECTION")
print("STATUS: SUCCESS")
print("=" * 70)