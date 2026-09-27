from ingestion.csv_ingest import load_flow_csv
from features.engine import calculate_features
from detectors.engine import analyze_dataframe
from alerts.store import save_alerts


print("CYBER-ASTRA pipeline starting...")

# Read-only ingestion
df = load_flow_csv("data/validation_flows.csv")

# Feature extraction
df = calculate_features(df)

# Threat detection
alerts = analyze_dataframe(df)

# Store standardized alerts
records = alerts.to_dict(orient="records")
save_alerts(records)

print("Pipeline complete.")
print("Flows analyzed:", len(df))
print("Alerts generated:", len(records))
print("Alert database: data/alerts.json")