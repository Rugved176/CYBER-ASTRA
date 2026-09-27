import pandas as pd
from dataclasses import dataclass, asdict
from datetime import datetime


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


def make_alert(
    row,
    threat_class,
    severity,
    confidence,
    evidence,
    ml_anomaly_score=0.0
):
    return Alert(
        timestamp=str(
            row.get(
                "timestamp",
                datetime.now().isoformat()
            )
        ),
        threat_class=threat_class,
        severity=severity,
        confidence=round(
            min(max(float(confidence), 0.0), 1.0),
            2
        ),
        src_ip=str(
            row.get("src_ip", "unknown")
        ),
        dst_ip=str(
            row.get("dst_ip", "unknown")
        ),
        evidence=evidence,
        flow_id=str(
            row.get("flow_id", "unknown")
        ),
        status="NEW",
        ml_anomaly_score=round(
            min(
                max(float(ml_anomaly_score), 0.0),
                1.0
            ),
            3
        )
    )


def detect_ddos(row):
    pps = float(row.get("packets_per_second", 0))
    bps = float(row.get("bytes_per_second", 0))
    packets = int(row.get("packets", 0))
    duration = float(row.get("duration", 0))

    if pps > 1000 or bps > 1_000_000:
        intensity_score = min(
            pps / 10000,
            1.0
        )

        confidence = (
            0.70 +
            intensity_score * 0.25
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
            f"{duration:.2f}s."
        )

    return None


def detect_c2_beaconing(row):
    interval_mean = float(
        row.get("inter_arrival_mean", 0)
    )

    interval_std = float(
        row.get("inter_arrival_std", 0)
    )

    if interval_mean <= 0 or interval_std <= 0:
        return None

    regularity = (
        interval_std /
        interval_mean
    )
    if regularity < 0.10:
        confidence = 0.82

        if regularity < 0.05:
            confidence = 0.90

        return make_alert(
            row,
            "Botnet C2 Beaconing",
            "MEDIUM",
            confidence,
            f"Highly regular flow timing detected. "
            f"Mean inter-arrival={interval_mean:.3f}s, "
            f"standard deviation={interval_std:.3f}s, "
            f"regularity ratio={regularity:.3f}."
        )

    return None


def detect_dns_anomaly(row):
    entropy = float(
        row.get("dns_entropy", 0)
    )

    query_length = int(
        row.get("dns_query_length", 0)
    )

    is_dns = int(
        row.get("is_dns", 0)
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
            f"query length={query_length}."
        )

    return None


def detect_encrypted_anomaly(row):
    protocol = str(
        row.get("protocol", "")
    ).upper()

    fingerprint = row.get(
        "tls_fingerprint",
        None
    )

    packets = int(
        row.get("packets", 0)
    )

    inter_arrival_mean = float(
        row.get("inter_arrival_mean", 0)
    )

    encrypted_protocol = protocol in {
        "TLS",
        "QUIC",
        "HTTPS"
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
        + ". Payload was not decrypted."
    )


def detect_recon(row):
    port_count = int(
        row.get("dst_port_count", 0)
    )

    host_count = int(
        row.get("dst_host_count", 0)
    )

    fanout = max(
        port_count,
        host_count
    )

    if fanout >= 20:
        confidence = min(
            0.95,
            0.65 + fanout / 100
        )

        return make_alert(
            row,
            "Reconnaissance / Port Scanning",
            "HIGH",
            confidence,
            f"Large destination fan-out detected: "
            f"{port_count} destination ports, "
            f"{host_count} destination hosts."
        )

    return None


def detect_exfiltration(row):
    ratio = float(
        row.get("byte_ratio", 0)
    )

    src_bytes = float(
        row.get("src_bytes", 0)
    )

    dst_bytes = float(
        row.get("dst_bytes", 0)
    )

    if ratio > 10 and src_bytes > 100_000:
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
            f"byte ratio={ratio:.2f}."
        )

    return None


def analyze_flow(row):
    detectors = [
        detect_ddos,
        detect_c2_beaconing,
        detect_dns_anomaly,
        detect_encrypted_anomaly,
        detect_recon,
        detect_exfiltration
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


def analyze_dataframe(df: pd.DataFrame):
    from ai.ml_detector import predict_anomaly

    all_alerts = []

    try:
        ml_df = predict_anomaly(df)

    except Exception:
        ml_df = df.copy()
        ml_df["ml_anomaly_score"] = 0.0

    for _, row in ml_df.iterrows():

        ml_score = float(
            row.get(
                "ml_anomaly_score",
                0.0
            )
        )

        alerts = analyze_flow(row)

        for alert in alerts:

            alert.ml_anomaly_score = round(
                min(
                    max(
                        ml_score,
                        0.0
                    ),
                    1.0
                ),
                3
            )

            all_alerts.append(
                alert.to_dict()
            )

    return pd.DataFrame(
        all_alerts
    )