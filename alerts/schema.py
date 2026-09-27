from typing import Literal

from pydantic import BaseModel, Field


class ThreatAlert(BaseModel):
    timestamp: str
    threat_class: str
    severity: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    ]

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    ml_anomaly_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0
    )

    src_ip: str
    dst_ip: str
    evidence: str
    flow_id: str = "unknown"

    status: Literal[
        "NEW",
        "INVESTIGATING",
        "RESOLVED"
    ] = "NEW"