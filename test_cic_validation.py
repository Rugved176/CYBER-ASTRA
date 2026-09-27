from dataset_adapters import CICIDS2017Adapter
from features.engine import calculate_features
from detectors.engine import analyze_dataframe

DATASET_ROOT = "data/sih_datasets/cic_ids2017"

print("=" * 70)
print("CYBER-ASTRA CIC-IDS2017 VALIDATION")
print("=" * 70)

adapter = CICIDS2017Adapter(DATASET_ROOT)

# Load a larger sample from every file
df = adapter.load(nrows_per_file=5000)

print("\n[1] DATASET")
print("Rows:", len(df))

print("\n[2] ORIGINAL LABEL DISTRIBUTION")
print(df["original_label"].value_counts())

print("\n[3] CYBER-ASTRA LABEL MAPPING")
print(df["threat_class"].value_counts())

# Feature engineering
features = calculate_features(df)

print("\n[4] FEATURE ENGINEERING")
print("Rows:", len(features))
print("Columns:", len(features.columns))

# Detection
detections = analyze_dataframe(features)

print("\n[5] DETECTION OUTPUT")
print("Detection rows:", len(detections))

print("\n[6] DETECTED THREAT DISTRIBUTION")
print(detections["threat_class"].value_counts())

print("\n[7] DETECTION SEVERITY")
print(detections["severity"].value_counts())

print("\n" + "=" * 70)
print("CIC-IDS2017 VALIDATION COMPLETE")
print("=" * 70)