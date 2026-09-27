from ingestion.csv_ingest import load_flow_csv
from features.engine import calculate_features
from detectors.engine import analyze_dataframe


# 1. Load passive traffic data
df = load_flow_csv("data/validation_flows.csv")

# 2. Calculate detection features
df = calculate_features(df)

# 3. Run all six detectors
alerts = analyze_dataframe(df)

print("\n=== CYBER-ASTRA DETECTION RESULT ===")

if alerts.empty:
    print("No threats detected.")
else:
    print(alerts.to_string(index=False))