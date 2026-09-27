from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from .common import DatasetAdapter


class CICIDS2018Adapter(DatasetAdapter):
    dataset_name = "CIC-IDS2018"

    def load_file(
        self,
        path: str | Path,
        nrows: int | None = None
    ) -> pd.DataFrame:

        path = Path(path)

        df = pd.read_csv(
            path,
            nrows=nrows,
            low_memory=False
        )

        # Clean column names
        df.columns = df.columns.astype(str).str.strip()

        # Clean labels
        df["Label"] = df["Label"].astype(str).str.strip()

        # Remove accidental header rows inside CSV
        df = df[df["Label"] != "Label"].copy()

        result = pd.DataFrame(index=df.index)

        # Metadata
        result["dataset_source"] = self.dataset_name
        result["dataset_file"] = path.name
        result["original_label"] = df["Label"]

        # Basic flow information
        result["timestamp"] = df["Timestamp"].astype(str)

        result["dst_port"] = pd.to_numeric(
            df["Dst Port"],
            errors="coerce"
        )

        # Protocol numbers → names
        protocol_numeric = pd.to_numeric(
            df["Protocol"],
            errors="coerce"
        )

        result["protocol"] = (
            protocol_numeric
            .map({
                6: "TCP",
                17: "UDP",
                1: "ICMP"
            })
            .fillna(df["Protocol"].astype(str))
        )

        # Duration: microseconds → seconds
        result["duration"] = (
            pd.to_numeric(
                df["Flow Duration"],
                errors="coerce"
            ) / 1_000_000.0
        )

        # Packets
        fwd_packets = pd.to_numeric(
            df["Tot Fwd Pkts"],
            errors="coerce"
        ).fillna(0)

        bwd_packets = pd.to_numeric(
            df["Tot Bwd Pkts"],
            errors="coerce"
        ).fillna(0)

        result["packets"] = fwd_packets + bwd_packets

        # Bytes
        result["src_bytes"] = pd.to_numeric(
            df["TotLen Fwd Pkts"],
            errors="coerce"
        ).fillna(0)

        result["dst_bytes"] = pd.to_numeric(
            df["TotLen Bwd Pkts"],
            errors="coerce"
        ).fillna(0)

        result["bytes_total"] = (
            result["src_bytes"] +
            result["dst_bytes"]
        )

        # Flow rates
        result["packets_per_second"] = pd.to_numeric(
            df["Flow Pkts/s"],
            errors="coerce"
        )

        result["bytes_per_second"] = pd.to_numeric(
            df["Flow Byts/s"],
            errors="coerce"
        )

        # Inter-arrival statistics
        result["inter_arrival_mean"] = (
            pd.to_numeric(
                df["Flow IAT Mean"],
                errors="coerce"
            ) / 1_000_000.0
        )

        result["inter_arrival_std"] = (
            pd.to_numeric(
                df["Flow IAT Std"],
                errors="coerce"
            ) / 1_000_000.0
        )

        # Fields unavailable in CIC-IDS2018 flow records
        result["src_ip"] = "UNKNOWN"
        result["dst_ip"] = "UNKNOWN"
        result["src_port"] = np.nan

        result["dst_port_count"] = np.nan
        result["dst_host_count"] = np.nan

        result["dns_query_length"] = np.nan
        result["dns_entropy"] = np.nan
        result["tls_fingerprint"] = np.nan

        # Useful TCP indicators
        result["syn_flag_count"] = pd.to_numeric(
            df["SYN Flag Cnt"],
            errors="coerce"
        )

        result["rst_flag_count"] = pd.to_numeric(
            df["RST Flag Cnt"],
            errors="coerce"
        )

        result["fwd_packets_per_second"] = pd.to_numeric(
            df["Fwd Pkts/s"],
            errors="coerce"
        )

        result["bwd_packets_per_second"] = pd.to_numeric(
            df["Bwd Pkts/s"],
            errors="coerce"
        )

        # Ground-truth label mapping
        result["threat_class"] = (
            result["original_label"]
            .map(self.map_label)
        )

        result["is_benign"] = (
            result["original_label"]
            .str.lower()
            == "benign"
        )

        return result

    @staticmethod
    def map_label(label: str) -> str:

        label = str(label).strip().lower()

        if label == "benign":
            return "BENIGN"

        if "dos attacks" in label:
            return "DDoS / Flooding"

        if "ddos" in label:
            return "DDoS / Flooding"

        if "infilteration" in label:
            return "Infiltration"

        if "infiltration" in label:
            return "Infiltration"

        return "OTHER"

    def load(
        self,
        nrows_per_file: int | None = None
    ) -> pd.DataFrame:

        csv_files = self.find_csv_files()

        if not csv_files:
            raise FileNotFoundError(
                f"No CSV files found in {self.root_dir}"
            )

        frames = []

        for csv_file in csv_files:

            print(f"Loading: {csv_file.name}")

            converted = self.load_file(
                csv_file,
                nrows=nrows_per_file
            )

            frames.append(converted)

        return pd.concat(
            frames,
            ignore_index=True
        )