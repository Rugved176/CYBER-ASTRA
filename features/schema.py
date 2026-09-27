from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TrafficFlow(BaseModel):

    model_config = ConfigDict(extra="ignore")

    timestamp: str

    flow_id: str = Field(
        default="unknown",
        min_length=1
    )

    src_ip: str
    dst_ip: str

    src_port: Optional[int] = Field(
        default=None,
        ge=0,
        le=65535
    )

    dst_port: Optional[int] = Field(
        default=None,
        ge=0,
        le=65535
    )

    protocol: Optional[str] = None

    duration: float = Field(
        default=0.0,
        ge=0
    )

    packets: int = Field(
        default=0,
        ge=0
    )

    bytes_total: int = Field(
        default=0,
        ge=0
    )

    packets_per_second: float = Field(
        default=0.0,
        ge=0
    )

    bytes_per_second: float = Field(
        default=0.0,
        ge=0
    )

    src_bytes: int = Field(
        default=0,
        ge=0
    )

    dst_bytes: int = Field(
        default=0,
        ge=0
    )

    src_entropy: float = Field(
        default=0.0,
        ge=0
    )

    dst_host_count: int = Field(
        default=0,
        ge=0
    )

    dst_port_count: int = Field(
        default=0,
        ge=0
    )

    dns_query_length: int = Field(
        default=0,
        ge=0
    )

    dns_entropy: float = Field(
        default=0.0,
        ge=0
    )

    inter_arrival_mean: float = Field(
        default=0.0,
        ge=0
    )

    inter_arrival_std: float = Field(
        default=0.0,
        ge=0
    )

    tls_fingerprint: Optional[str] = None