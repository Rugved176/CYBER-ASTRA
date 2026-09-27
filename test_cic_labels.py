from pathlib import Path
import pandas as pd

root = Path("data/sih_datasets/cic_ids2017")

for csv_file in sorted(root.rglob("*.csv")):
    print("\n" + "=" * 70)
    print(csv_file.name)

    df = pd.read_csv(
        csv_file,
        low_memory=False,
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    df["Label"] = (
        df["Label"]
        .astype(str)
        .str.strip()
    )

    print("Rows:", len(df))

    print("\nAll labels:")
    print(df["Label"].value_counts())

    print("\nMapped CYBER-ASTRA classes:")

    def map_label(label):
        label = str(label).strip().lower()

        if label == "benign":
            return "BENIGN"

        if "ddos" in label:
            return "DDoS / Flooding"

        if label.startswith("dos "):
            return "DDoS / Flooding"

        if "portscan" in label or "port scan" in label:
            return "Reconnaissance / Port Scanning"

        if label == "bot":
            return "Botnet C2 Beaconing"

        if "infiltration" in label:
            return "Infiltration"

        if "web attack" in label:
            return "Web Attack"

        if "ftp-patator" in label:
            return "FTP-Patator"

        if "ssh-patator" in label:
            return "SSH-Patator"

        if "heartbleed" in label:
            return "Heartbleed"

        return "OTHER"

    mapped = df["Label"].map(map_label)

    print(mapped.value_counts())