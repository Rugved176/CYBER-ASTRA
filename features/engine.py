import pandas as pd
import numpy as np


def calculate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw network-flow observations into
    detection-ready statistical features.

    This function only analyzes supplied data.
    It does not generate or send network traffic.
    """

    result = df.copy()

    # ---------------------------------------------------------
    # Basic numeric cleanup
    # ---------------------------------------------------------
    result["duration"] = pd.to_numeric(
        result["duration"],
        errors="coerce"
    ).fillna(0)

    result["packets"] = pd.to_numeric(
        result["packets"],
        errors="coerce"
    ).fillna(0)

    result["bytes_total"] = pd.to_numeric(
        result["bytes_total"],
        errors="coerce"
    ).fillna(0)

    # ---------------------------------------------------------
    # Traffic-rate features
    # ---------------------------------------------------------
    safe_duration = result["duration"].where(
        result["duration"] >= 0.01,
        np.nan
    )

    calculated_pps = (
        result["packets"] / safe_duration
    ).replace(
        [np.inf, -np.inf],
        np.nan
    )

    calculated_bps = (
        result["bytes_total"] / safe_duration
    ).replace(
        [np.inf, -np.inf],
        np.nan
    )

    # Preserve dataset-provided rates when available.
    if "packets_per_second" in result.columns:
        result["packets_per_second"] = pd.to_numeric(
            result["packets_per_second"],
            errors="coerce"
        ).fillna(calculated_pps)

    else:
        result["packets_per_second"] = calculated_pps

    if "bytes_per_second" in result.columns:
        result["bytes_per_second"] = pd.to_numeric(
            result["bytes_per_second"],
            errors="coerce"
        ).fillna(calculated_bps)

    else:
        result["bytes_per_second"] = calculated_bps

    result["packets_per_second"] = (
        result["packets_per_second"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    result["bytes_per_second"] = (
        result["bytes_per_second"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    # ---------------------------------------------------------
    # Source/destination byte estimates
    # ---------------------------------------------------------
    if "src_bytes" not in result.columns:
        result["src_bytes"] = result["bytes_total"]

    if "dst_bytes" not in result.columns:
        result["dst_bytes"] = 0

    result["src_bytes"] = pd.to_numeric(
        result["src_bytes"],
        errors="coerce"
    ).fillna(0)

    result["dst_bytes"] = pd.to_numeric(
        result["dst_bytes"],
        errors="coerce"
    ).fillna(0)

    result["byte_ratio"] = (
        result["src_bytes"] /
        result["dst_bytes"].replace(0, np.nan)
    ).replace(
        [np.inf, -np.inf],
        np.nan
    ).fillna(0)

    # ---------------------------------------------------------
    # Port / protocol indicators
    # ---------------------------------------------------------
    result["is_common_web_port"] = (
        result["dst_port"].isin([80, 443])
    ).astype(int)

    result["is_dns"] = (
        result["dst_port"] == 53
    ).astype(int)

    result["is_tcp"] = (
        result["protocol"].astype(str).str.upper() == "TCP"
    ).astype(int)

    result["is_udp"] = (
        result["protocol"].astype(str).str.upper() == "UDP"
    ).astype(int)

    # ---------------------------------------------------------
    # Flow intensity
    # ---------------------------------------------------------
    result["flow_intensity"] = (
        result["packets_per_second"] +
        result["bytes_per_second"] / 1000
    )

    # ---------------------------------------------------------
    # Timing-quality indicator
    # ---------------------------------------------------------
    result["valid_timing"] = (
        (result["inter_arrival_mean"].fillna(0) > 0) &
        (result["inter_arrival_std"].fillna(0) > 0)
    ).astype(int)

    return result