from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .common import DatasetAdapter


class BOTIoTAdapter(DatasetAdapter):
    """
    Adapter for the BoT-IoT 10-best-features dataset.

    Converts BoT-IoT records into the common CYBER-ASTRA
    flow representation while preserving the original
    BoT-IoT labels and dataset-specific behavioral features.

    Important:
    The BoT-IoT 10-best feature set does not directly provide
    packet totals, byte totals, flow duration, DNS entropy,
    TLS fingerprints, or destination fan-out.

    Therefore, unavailable CYBER-ASTRA fields remain NaN rather
    than being fabricated from unrelated dataset fields.
    """

    dataset_name = "BoT-IoT"

    def load_file(
        self,
        path: str | Path,
        nrows: int | None = None,
    ) -> pd.DataFrame:

        path = Path(path)

        df = pd.read_csv(
            path,
            nrows=nrows,
            low_memory=False,
        )

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        result = pd.DataFrame(index=df.index)

        # ============================================================
        # DATASET METADATA
        # ============================================================

        result["dataset_source"] = self.dataset_name
        result["dataset_file"] = path.name

        # ============================================================
        # ORIGINAL BOT-IOT LABELS
        # ============================================================

        result["original_label"] = (
            df["category"]
            .astype(str)
            .str.strip()
        )

        result["original_subcategory"] = (
            df["subcategory"]
            .astype(str)
            .str.strip()
        )

        result["attack"] = pd.to_numeric(
            df["attack"],
            errors="coerce",
        )

        # ============================================================
        # FLOW IDENTITY
        # ============================================================

        result["flow_id"] = (
            df["pkSeqID"]
            .astype(str)
        )

        # ============================================================
        # NETWORK INFORMATION
        # ============================================================

        result["src_ip"] = (
            df["saddr"]
            .astype(str)
        )

        result["dst_ip"] = (
            df["daddr"]
            .astype(str)
        )

        result["src_port"] = pd.to_numeric(
            df["sport"],
            errors="coerce",
        )

        result["dst_port"] = pd.to_numeric(
            df["dport"],
            errors="coerce",
        )

        result["protocol"] = (
            df["proto"]
            .astype(str)
            .str.upper()
        )

        # ============================================================
        # BOT-IOT TIMING FEATURES
        # ============================================================

        result["inter_arrival_mean"] = pd.to_numeric(
            df["mean"],
            errors="coerce",
        )

        result["inter_arrival_std"] = pd.to_numeric(
            df["stddev"],
            errors="coerce",
        )

        result["inter_arrival_min"] = pd.to_numeric(
            df["min"],
            errors="coerce",
        )

        result["inter_arrival_max"] = pd.to_numeric(
            df["max"],
            errors="coerce",
        )

        # ============================================================
        # BOT-IOT RATE FEATURES
        #
        # Keep the original semantics.
        # Do NOT pretend these are generic bytes/sec or packets/sec.
        # ============================================================

        result["src_rate"] = pd.to_numeric(
            df["srate"],
            errors="coerce",
        )

        result["dst_rate"] = pd.to_numeric(
            df["drate"],
            errors="coerce",
        )

        # Dataset-specific derived rate indicators.
        #
        # These are explicitly named as BoT-IoT features so that
        # downstream detectors do not confuse them with generic
        # CYBER-ASTRA packets/sec or bytes/sec.

        result["bot_iot_rate_max"] = (
            result[["src_rate", "dst_rate"]]
            .max(axis=1)
        )

        result["bot_iot_rate_sum"] = (
            result["src_rate"].fillna(0)
            + result["dst_rate"].fillna(0)
        )

        # ============================================================
        # CONNECTION-COUNT FEATURES
        # ============================================================

        result["src_connection_count"] = pd.to_numeric(
            df["N_IN_Conn_P_SrcIP"],
            errors="coerce",
        )

        result["dst_connection_count"] = pd.to_numeric(
            df["N_IN_Conn_P_DstIP"],
            errors="coerce",
        )

        # Useful behavioral indicator for high connection activity.
        result["bot_iot_connection_max"] = (
            result[
                [
                    "src_connection_count",
                    "dst_connection_count",
                ]
            ].max(axis=1)
        )

        result["bot_iot_connection_sum"] = (
            result["src_connection_count"].fillna(0)
            + result["dst_connection_count"].fillna(0)
        )

        # ============================================================
        # ADDITIONAL BOT-IOT TIMING FEATURES
        # ============================================================

        # Preserve the original min/max timing information while
        # providing a simple timing-span feature.
        result["bot_iot_inter_arrival_range"] = (
            result["inter_arrival_max"]
            - result["inter_arrival_min"]
        )

        # ============================================================
        # FIELDS NOT AVAILABLE IN 10-BEST BOT-IOT DATA
        #
        # Keep these as NaN.
        # Never fabricate them.
        # ============================================================

        result["timestamp"] = pd.NaT

        result["duration"] = np.nan
        result["packets"] = np.nan
        result["bytes_total"] = np.nan

        result["packets_per_second"] = np.nan
        result["bytes_per_second"] = np.nan

        result["src_bytes"] = np.nan
        result["dst_bytes"] = np.nan

        result["src_entropy"] = np.nan

        result["dst_host_count"] = np.nan
        result["dst_port_count"] = np.nan

        result["dns_query_length"] = np.nan
        result["dns_entropy"] = np.nan

        result["tls_fingerprint"] = np.nan

        # ============================================================
        # CYBER-ASTRA THREAT MAPPING
        # ============================================================

        result["threat_class"] = (
            result["original_label"]
            .map(self.map_label)
        )

        result["is_benign"] = (
            result["original_label"]
            .str.upper()
            == "NORMAL"
        )

        return result

    @staticmethod
    def map_label(label: str) -> str:

        label = (
            str(label)
            .strip()
            .lower()
        )

        if label == "normal":
            return "BENIGN"

        if label == "ddos":
            return "DDoS / Flooding"

        if label == "reconnaissance":
            return "Reconnaissance / Port Scanning"

        if label == "data_exfiltration":
            return "Data Exfiltration"

        # These BoT-IoT categories are intentionally not
        # forced into one of the six CYBER-ASTRA classes.

        if label == "dos":
            return "OTHER"

        if label == "theft":
            return "OTHER"

        return "OTHER"

    def load(
        self,
        nrows_per_file: int | None = None,
    ) -> pd.DataFrame:

        csv_files = sorted(
            self.root_dir.glob(
                "UNSW_2018_IoT_Botnet_Final_10_best_*.csv"
            )
        )

        if not csv_files:
            raise FileNotFoundError(
                f"No BoT-IoT CSV files found in {self.root_dir}"
            )

        frames = []

        for csv_file in csv_files:

            print(
                f"Loading BoT-IoT: "
                f"{csv_file.name}"
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