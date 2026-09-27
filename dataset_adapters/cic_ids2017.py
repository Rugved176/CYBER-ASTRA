from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .common import DatasetAdapter


class CICIDS2017Adapter(DatasetAdapter):
    dataset_name = "CIC-IDS2017"

    def load_file(
        self,
        path: str | Path,
        nrows: int | None = None,
    ) -> pd.DataFrame:

        df = pd.read_csv(
            path,
            nrows=nrows,
            low_memory=False,
        )

        # Normalize column names
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        # Clean label
        df["Label"] = (
            df["Label"]
            .astype(str)
            .str.strip()
        )

        result = pd.DataFrame(index=df.index)

        # Dataset information
        result["dataset_source"] = self.dataset_name
        result["dataset_file"] = Path(path).name
        result["original_label"] = df["Label"]

        # ---------------------------------------------------------
        # Core flow features
        # ---------------------------------------------------------

        result["dst_port"] = pd.to_numeric(
            df["Destination Port"],
            errors="coerce",
        )

        result["duration"] = (
            pd.to_numeric(
                df["Flow Duration"],
                errors="coerce",
            )
            / 1_000_000.0
        )

        result["packets"] = (
            pd.to_numeric(
                df["Total Fwd Packets"],
                errors="coerce",
            )
            +
            pd.to_numeric(
                df["Total Backward Packets"],
                errors="coerce",
            )
        )

        result["src_bytes"] = pd.to_numeric(
            df["Total Length of Fwd Packets"],
            errors="coerce",
        )

        result["dst_bytes"] = pd.to_numeric(
            df["Total Length of Bwd Packets"],
            errors="coerce",
        )

        result["bytes_total"] = (
            result["src_bytes"]
            + result["dst_bytes"]
        )

        result["packets_per_second"] = pd.to_numeric(
            df["Flow Packets/s"],
            errors="coerce",
        )

        result["bytes_per_second"] = pd.to_numeric(
            df["Flow Bytes/s"],
            errors="coerce",
        )

        result["inter_arrival_mean"] = (
            pd.to_numeric(
                df["Flow IAT Mean"],
                errors="coerce",
            )
            / 1_000_000.0
        )

        result["inter_arrival_std"] = (
            pd.to_numeric(
                df["Flow IAT Std"],
                errors="coerce",
            )
            / 1_000_000.0
        )

        # ---------------------------------------------------------
        # Features not directly available in CIC-IDS2017 CSV
        # ---------------------------------------------------------

        result["dst_port_count"] = np.nan
        result["dst_host_count"] = np.nan
        result["dns_query_length"] = np.nan
        result["dns_entropy"] = np.nan
        result["tls_fingerprint"] = np.nan

        # IP information is not available in this CSV
        result["src_ip"] = "UNKNOWN"
        result["dst_ip"] = "UNKNOWN"
        result["src_port"] = np.nan
        result["protocol"] = "UNKNOWN"

        # ---------------------------------------------------------
        # Additional CIC-IDS2017 features
        # ---------------------------------------------------------

        result["syn_flag_count"] = pd.to_numeric(
            df["SYN Flag Count"],
            errors="coerce",
        )

        result["rst_flag_count"] = pd.to_numeric(
            df["RST Flag Count"],
            errors="coerce",
        )

        result["fwd_packets_per_second"] = pd.to_numeric(
            df["Fwd Packets/s"],
            errors="coerce",
        )

        result["bwd_packets_per_second"] = pd.to_numeric(
            df["Bwd Packets/s"],
            errors="coerce",
        )

        # ---------------------------------------------------------
        # CYBER-ASTRA threat mapping
        # ---------------------------------------------------------

        result["threat_class"] = (
            result["original_label"]
            .map(self.map_label)
        )

        result["is_benign"] = (
            result["original_label"]
            .str.upper()
            == "BENIGN"
        )

        return result

    @staticmethod
    def map_label(label: str) -> str:

        label = str(label).strip().lower()

        # ---------------------------------------------------------
        # Normal traffic
        # ---------------------------------------------------------

        if label == "benign":
            return "BENIGN"

        # ---------------------------------------------------------
        # CYBER-ASTRA primary threat classes
        # ---------------------------------------------------------

        # DDoS
        if "ddos" in label:
            return "DDoS / Flooding"

        # DoS variants
        if label.startswith("dos "):
            return "DDoS / Flooding"

        # Port scanning
        if "portscan" in label or "port scan" in label:
            return "Reconnaissance / Port Scanning"

        # Bot traffic
        if label == "bot":
            return "Botnet C2 Beaconing"

        # ---------------------------------------------------------
        # Other CIC-IDS2017 attack families
        # Preserve them rather than incorrectly assigning them
        # to one of the six SIH threat classes.
        # ---------------------------------------------------------

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

        # Unknown label
        return "OTHER"

    def load(
        self,
        nrows_per_file: int | None = None,
    ) -> pd.DataFrame:

        csv_files = self.find_csv_files()

        if not csv_files:
            raise FileNotFoundError(
                f"No CSV files found in {self.root_dir}"
            )

        frames = []

        for csv_file in csv_files:

            print(
                f"Loading: {csv_file.name}"
            )

            converted = self.load_file(
                csv_file,
                nrows=nrows_per_file,
            )

            frames.append(converted)

        return pd.concat(
            frames,
            ignore_index=True,
        )