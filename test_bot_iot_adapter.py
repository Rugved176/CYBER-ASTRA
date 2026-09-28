from dataset_adapters import BOTIoTAdapter

DATASET_ROOT = "data/sih_datasets/bot_iot"

print("=" * 70)
print("CYBER-ASTRA BoT-IoT ADAPTER TEST")
print("=" * 70)

adapter = BOTIoTAdapter(DATASET_ROOT)

df = adapter.load(
    nrows_per_file=100
)

print("\n[1] DATASET")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\n[2] DATASET SOURCE")
print(df["dataset_source"].value_counts())

print("\n[3] ORIGINAL CATEGORIES")
print(df["original_label"].value_counts())

print("\n[4] ORIGINAL SUBCATEGORIES")
print(df["original_subcategory"].value_counts())

print("\n[5] CYBER-ASTRA MAPPING")
print(df["threat_class"].value_counts())

print("\n[6] SAMPLE")
print(
    df[
        [
            "flow_id",
            "src_ip",
            "dst_ip",
            "src_port",
            "dst_port",
            "protocol",
            "original_label",
            "original_subcategory",
            "threat_class",
        ]
    ].head(10).to_string(index=False)
)

print("\n" + "=" * 70)
print("STATUS: ADAPTER TEST COMPLETE")
print("=" * 70)