import pandas as pd
from dataclasses import dataclass, asdict
from datetime import datetime


# ============================================================
# ALERT DATA MODEL
# ============================================================

@dataclass
class Alert:
    timestamp: str
    threat_class: str
    severity: str
    confidence: float
    src_ip: str
    dst_ip: str
    evidence: str
    flow_id: str = "unknown"
    status: str = "NEW"
    ml_anomaly_score: float = 0.0

    def to_dict(self):
        return asdict(self)


# ============================================================
# ALERT CREATION
# ============================================================

def make_alert(
    row,
    threat_class,
    severity,
    confidence,
    evidence,
    ml_anomaly_score=0.0,
):
    return Alert(
        timestamp=str(
            row.get(
                "timestamp",
                datetime.now().isoformat(),
            )
        ),
        threat_class=threat_class,
        severity=severity,
        confidence=round(
            min(max(float(confidence), 0.0), 1.0),
            2,
        ),
        src_ip=str(
            row.get(
                "src_ip",
                "unknown",
            )
        ),
        dst_ip=str(
            row.get(
                "dst_ip",
                "unknown",
            )
        ),
        evidence=evidence,
        flow_id=str(
            row.get(
                "flow_id",
                "unknown",
            )
        ),
        status="NEW",
        ml_anomaly_score=round(
            min(max(float(ml_anomaly_score), 0.0), 1.0),
            3,
        ),
    )


# ============================================================
# 1. DDOS / FLOODING
# ============================================================

def detect_ddos(row):

    pps = float(
        row.get(
            "packets_per_second",
            0,
        )
    )

    bps = float(
        row.get(
            "bytes_per_second",
            0,
        )
    )

    packets = int(
        row.get(
            "packets",
            0,
        )
    )

    duration = float(
        row.get(
            "duration",
            0,
        )
    )

    if pps > 1000 or bps > 1_000_000:

        intensity_score = min(
            pps / 10000,
            1.0,
        )

        confidence = (
            0.70
            + intensity_score * 0.25
        )

        severity = "HIGH"

        if pps > 5000 or bps > 5_000_000:
            severity = "CRITICAL"

        return make_alert(
            row,
            "Volumetric / Protocol DDoS",
            severity,
            confidence,
            f"High traffic intensity detected: "
            f"{pps:.1f} packets/sec, "
            f"{bps:.0f} bytes/sec, "
            f"{packets} packets over "
            f"{duration:.2f}s.",
        )

    return None


# ============================================================
# 1B. BoT-IoT BEHAVIOR-LEVEL DDOS
# ============================================================

def detect_bot_iot_ddos_dataframe(df):
    """
    Behavior-level DDoS detector for BoT-IoT-style features.

    Uses only behavioral features available in the
    BoT-IoT 10-best-feature subset.

    Ground-truth labels are NOT used.

    Signals:
        - sustained high connection activity
        - elevated traffic rate
        - non-reconnaissance timing behavior
        - repeated observations from the same source
    """

    required = {
        "src_ip",
        "bot_iot_rate_sum",
        "bot_iot_connection_sum",
        "inter_arrival_mean",
    }

    if not required.issubset(df.columns):
        return []

    work = df.copy()

    numeric_columns = [
        "bot_iot_rate_sum",
        "bot_iot_connection_sum",
        "inter_arrival_mean",
    ]

    for column in numeric_columns:
        work[column] = pd.to_numeric(
            work[column],
            errors="coerce",
        )

    alerts = []

    for src_ip, group in work.groupby("src_ip"):

        if str(src_ip).upper() in {
            "UNKNOWN",
            "NAN",
            "NONE",
        }:
            continue

        # Require repeated observations from a source.
        if len(group) < 3:
            continue

        median_rate = float(
            group["bot_iot_rate_sum"].median()
        )

        max_rate = float(
            group["bot_iot_rate_sum"].max()
        )

        median_connections = float(
            group["bot_iot_connection_sum"].median()
        )

        median_iat = float(
            group["inter_arrival_mean"].median()
        )

        score = 0.0
        evidence_parts = []

        # BoT-IoT DDoS shows very high connection activity.
        if median_connections >= 190:

            score += 0.45

            evidence_parts.append(
                f"median connection activity={median_connections:.0f}"
            )

        elif median_connections >= 170:

            score += 0.30

            evidence_parts.append(
                f"median connection activity={median_connections:.0f}"
            )

        # DDoS rate in this feature subset is generally
        # modest, so use a low behavioral threshold.
        if median_rate >= 0.30:

            score += 0.30

            evidence_parts.append(
                f"median traffic rate={median_rate:.3f}"
            )

        elif max_rate >= 1.0:

            score += 0.15

            evidence_parts.append(
                f"peak traffic rate={max_rate:.3f}"
            )

        # Larger inter-arrival values support sustained
        # volumetric behavior rather than rapid scanning.
        if (
            not pd.isna(median_iat)
            and median_iat >= 0.5
        ):

            score += 0.25

            evidence_parts.append(
                f"median inter-arrival={median_iat:.3f}s"
            )

        # Require multiple independent behavioral signals.
        if score < 0.70:
            continue

        confidence = min(
            0.95,
            0.55 + (score * 0.45),
        )

        representative = group.iloc[0]

        alerts.append(
            make_alert(
                representative,
                "Volumetric / Protocol DDoS",
                "HIGH",
                confidence,
                "BoT-IoT behavioral DDoS pattern: "
                + ", ".join(evidence_parts)
                + ".",
            )
        )

    return alerts


# ============================================================
# 2. C2 BEACONING
# ============================================================

def detect_c2_beaconing_dataframe(df):
    """
    Behavior-level C2 beaconing detector.

    Uses repeated source-to-destination communication
    and periodic inter-arrival timing.

    Ground-truth labels are NOT used.
    """

    required = {
        "src_ip",
        "dst_ip",
        "inter_arrival_mean",
        "inter_arrival_std",
    }

    if not required.issubset(df.columns):
        return []

    work = df.copy()

    work["inter_arrival_mean"] = pd.to_numeric(
        work["inter_arrival_mean"],
        errors="coerce",
    )

    work["inter_arrival_std"] = pd.to_numeric(
        work["inter_arrival_std"],
        errors="coerce",
    )

    alerts = []

    for (
        src_ip,
        dst_ip,
    ), group in work.groupby(
        ["src_ip", "dst_ip"]
    ):

        if str(src_ip).upper() in {
            "UNKNOWN",
            "NAN",
            "NONE",
        }:
            continue

        if str(dst_ip).upper() in {
            "UNKNOWN",
            "NAN",
            "NONE",
        }:
            continue

        if len(group) < 5:
            continue

        mean_iat = float(
            group["inter_arrival_mean"].median()
        )

        std_iat = float(
            group["inter_arrival_std"].median()
        )

        if pd.isna(mean_iat) or pd.isna(std_iat):
            continue

        if mean_iat <= 0:
            continue

        # Low relative timing variation suggests periodic activity.
        periodicity_ratio = (
            std_iat / mean_iat
        )

        if periodicity_ratio > 0.35:
            continue

        confidence = min(
            0.95,
            0.70
            + max(
                0.0,
                0.35 - periodicity_ratio,
            ),
        )

        representative = group.iloc[0]

        alerts.append(
            make_alert(
                representative,
                "Botnet C2 Beaconing",
                "MEDIUM",
                confidence,
                "Repeated periodic communication pattern: "
                f"median inter-arrival={mean_iat:.3f}s, "
                f"timing variation ratio={periodicity_ratio:.3f}, "
                f"observations={len(group)}.",
            )
        )

    return alerts


# ============================================================
# 3. DGA / DNS TUNNELLING
# ============================================================

def detect_dns_anomaly(row):

    entropy = float(
        row.get(
            "dns_entropy",
            0,
        )
    )

    query_length = int(
        row.get(
            "dns_query_length",
            0,
        )
    )

    is_dns = int(
        row.get(
            "is_dns",
            0,
        )
    )

    if is_dns == 0 and query_length == 0:
        return None

    if entropy > 4.0 or query_length > 60:

        confidence = 0.80

        if entropy > 5.0 or query_length > 100:
            confidence = 0.92

        severity = "MEDIUM"

        if entropy > 5.0 or query_length > 100:
            severity = "HIGH"

        return make_alert(
            row,
            "DGA Domains / DNS Tunnelling",
            severity,
            confidence,
            f"Suspicious DNS characteristics: "
            f"entropy={entropy:.2f}, "
            f"query length={query_length}.",
        )

    return None


# ============================================================
# 4. MALWARE IN ENCRYPTED SESSIONS
# ============================================================

def detect_encrypted_anomaly(row):

    protocol = str(
        row.get(
            "protocol",
            "",
        )
    ).upper()

    fingerprint = row.get(
        "tls_fingerprint",
        None,
    )

    packets = int(
        row.get(
            "packets",
            0,
        )
    )

    inter_arrival_mean = float(
        row.get(
            "inter_arrival_mean",
            0,
        )
    )

    encrypted_protocol = protocol in {
        "TLS",
        "QUIC",
        "HTTPS",
    }

    if not encrypted_protocol:
        return None

    evidence_parts = []

    if fingerprint:
        evidence_parts.append(
            f"TLS fingerprint={fingerprint}"
        )

    if packets > 0:
        evidence_parts.append(
            f"packet count={packets}"
        )

    if inter_arrival_mean > 0:
        evidence_parts.append(
            f"mean timing={inter_arrival_mean:.3f}s"
        )

    if not evidence_parts:
        return None

    return make_alert(
        row,
        "Malware in Encrypted Session",
        "MEDIUM",
        0.70,
        "Encrypted-session metadata anomaly observed: "
        + ", ".join(evidence_parts)
        + ". Payload was not decrypted.",
    )


# ============================================================
# 5. RECONNAISSANCE / PORT SCANNING
# ============================================================

def detect_recon(row):

    port_count = int(
        row.get(
            "dst_port_count",
            0,
        )
    )

    host_count = int(
        row.get(
            "dst_host_count",
            0,
        )
    )

    fanout = max(
        port_count,
        host_count,
    )

    if fanout >= 20:

        confidence = min(
            0.95,
            0.65 + fanout / 100,
        )

        return make_alert(
            row,
            "Reconnaissance / Port Scanning",
            "HIGH",
            confidence,
            f"Large destination fan-out detected: "
            f"{port_count} destination ports, "
            f"{host_count} destination hosts.",
        )

    return None


def detect_reconnaissance_dataframe(df):
    """
    Behavior-level reconnaissance detector.

    Reconnaissance requires destination diversity together
    with rapid probing behavior.

    High destination diversity alone is not sufficient,
    because sustained volumetric traffic can touch multiple
    ports or hosts over a long observation period.

    Signals:
        - destination-port diversity
        - destination-host diversity
        - rapid repeated activity

    Ground-truth fields are NOT used.
    """

    required = {
        "src_ip",
        "dst_ip",
        "dst_port",
        "inter_arrival_mean",
        "inter_arrival_std",
    }

    if not required.issubset(df.columns):
        return []

    work = df.copy()

    work["inter_arrival_mean"] = pd.to_numeric(
        work["inter_arrival_mean"],
        errors="coerce",
    )

    work["inter_arrival_std"] = pd.to_numeric(
        work["inter_arrival_std"],
        errors="coerce",
    )

    work["dst_port"] = pd.to_numeric(
        work["dst_port"],
        errors="coerce",
    )

    alerts = []

    for src_ip, group in work.groupby("src_ip"):

        if str(src_ip).upper() in {
            "UNKNOWN",
            "NAN",
            "NONE",
        }:
            continue

        # Require repeated observations.
        if len(group) < 3:
            continue

        unique_ports = (
            group["dst_port"]
            .dropna()
            .nunique()
        )

        unique_hosts = (
            group["dst_ip"]
            .dropna()
            .nunique()
        )

        mean_iat = float(
            group["inter_arrival_mean"]
            .median()
        )

        # ----------------------------------------------------
        # RECON BEHAVIOR
        # ----------------------------------------------------

        port_scan = unique_ports >= 5
        host_scan = unique_hosts >= 3

        rapid_activity = (
            not pd.isna(mean_iat)
            and mean_iat >= 0
            and mean_iat < 0.01
        )

        # High port/host diversity alone can occur during DDoS.
        # Require rapid probing for dataframe-level recon.
        port_scan_behavior = (
            port_scan
            and rapid_activity
        )

        host_scan_behavior = (
            host_scan
            and rapid_activity
        )

        if (
            not port_scan_behavior
            and not host_scan_behavior
        ):
            continue

        score = 0.0
        evidence_parts = []

        # ----------------------------------------------------
        # PORT DIVERSITY
        # ----------------------------------------------------

        if (
            port_scan_behavior
            and unique_ports >= 10
        ):

            score += 0.45

            evidence_parts.append(
                f"{unique_ports} unique destination ports"
            )

        elif (
            port_scan_behavior
            and unique_ports >= 5
        ):

            score += 0.30

            evidence_parts.append(
                f"{unique_ports} unique destination ports"
            )

        # ----------------------------------------------------
        # HOST DIVERSITY
        # ----------------------------------------------------

        if (
            host_scan_behavior
            and unique_hosts >= 10
        ):

            score += 0.45

            evidence_parts.append(
                f"{unique_hosts} unique destination hosts"
            )

        elif (
            host_scan_behavior
            and unique_hosts >= 3
        ):

            score += 0.30

            evidence_parts.append(
                f"{unique_hosts} unique destination hosts"
            )

        # ----------------------------------------------------
        # RAPID PROBING
        # ----------------------------------------------------

        if rapid_activity:

            score += 0.25

            evidence_parts.append(
                f"median inter-arrival={mean_iat:.6f}s"
            )

        # ----------------------------------------------------
        # FINAL THRESHOLD
        # ----------------------------------------------------

        if score < 0.55:
            continue

        confidence = min(
            0.95,
            0.60 + score * 0.35,
        )

        representative = group.iloc[0]

        alerts.append(
            make_alert(
                representative,
                "Reconnaissance / Port Scanning",
                "HIGH",
                confidence,
                "Behavior-level reconnaissance pattern: "
                + ", ".join(evidence_parts)
                + ".",
            )
        )

    return alerts


# ============================================================
# 6. DATA EXFILTRATION
# ============================================================

def detect_exfiltration(row):

    ratio = float(
        row.get(
            "byte_ratio",
            0,
        )
    )

    src_bytes = float(
        row.get(
            "src_bytes",
            0,
        )
    )

    dst_bytes = float(
        row.get(
            "dst_bytes",
            0,
        )
    )

    if (
        ratio > 10
        and src_bytes > 100_000
    ):

        confidence = 0.85

        if src_bytes > 1_000_000:
            confidence = 0.92

        return make_alert(
            row,
            "Data Exfiltration",
            "HIGH",
            confidence,
            f"Unusual outbound traffic asymmetry: "
            f"{src_bytes:.0f} source bytes, "
            f"{dst_bytes:.0f} destination bytes, "
            f"byte ratio={ratio:.2f}.",
        )

    return None


# ============================================================
# FLOW-LEVEL ANALYSIS
# ============================================================

def analyze_flow(row):

    detectors = [
        detect_ddos,
        detect_dns_anomaly,
        detect_encrypted_anomaly,
        detect_recon,
        detect_exfiltration,
    ]

    alerts = []

    for detector in detectors:

        try:

            alert = detector(row)

            if alert is not None:
                alerts.append(alert)

        except Exception:
            continue

    return alerts


# ============================================================
# DATAFRAME-LEVEL ANALYSIS
# ============================================================

def analyze_dataframe(
    df: pd.DataFrame,
):

    from ai.ml_detector import predict_anomaly

    all_alerts = []

    # --------------------------------------------------------
    # ML ANOMALY DETECTION
    # --------------------------------------------------------

    try:

        ml_df = predict_anomaly(df)

    except Exception:

        ml_df = df.copy()

        ml_df["ml_anomaly_score"] = 0.0

    # --------------------------------------------------------
    # FLOW-LEVEL DETECTORS
    # --------------------------------------------------------

    for _, row in ml_df.iterrows():

        ml_score = float(
            row.get(
                "ml_anomaly_score",
                0.0,
            )
        )

        alerts = analyze_flow(
            row
        )

        for alert in alerts:

            alert.ml_anomaly_score = round(
                min(
                    max(
                        ml_score,
                        0.0,
                    ),
                    1.0,
                ),
                3,
            )

            all_alerts.append(
                alert.to_dict()
            )

    # --------------------------------------------------------
    # BEHAVIOR-LEVEL C2 DETECTION
    # --------------------------------------------------------

    try:

        c2_alerts = (
            detect_c2_beaconing_dataframe(
                ml_df
            )
        )

        for alert in c2_alerts:

            all_alerts.append(
                alert.to_dict()
            )

    except Exception:
        pass

    # --------------------------------------------------------
    # BEHAVIOR-LEVEL BoT-IoT DDOS DETECTION
    # --------------------------------------------------------

    try:

        bot_iot_ddos_alerts = (
            detect_bot_iot_ddos_dataframe(
                ml_df
            )
        )

        for alert in bot_iot_ddos_alerts:

            all_alerts.append(
                alert.to_dict()
            )

    except Exception:
        pass

    # --------------------------------------------------------
    # BEHAVIOR-LEVEL RECONNAISSANCE
    # --------------------------------------------------------

    try:

        recon_alerts = (
            detect_reconnaissance_dataframe(
                ml_df
            )
        )

        for alert in recon_alerts:

            all_alerts.append(
                alert.to_dict()
            )

    except Exception:
        pass

    # --------------------------------------------------------
    # RETURN ALERT DATAFRAME
    # --------------------------------------------------------

    if not all_alerts:

        return pd.DataFrame()

    return pd.DataFrame(
        all_alerts
    )