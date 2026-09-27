import math
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from features.schema import TrafficFlow


REQUIRED_COLUMNS = [
    "timestamp",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "protocol",
    "duration",
    "packets",
    "bytes_total",
]


def _clean_value(value):
    """Convert pandas/numpy missing values into Python None."""

    if value is None:
        return None

    if isinstance(value, (float, np.floating)) and math.isnan(value):
        return None

    if pd.isna(value):
        return None

    if isinstance(value, np.generic):
        return value.item()

    return value


def _normalize_record(record):
    """Clean and normalize one traffic-flow record."""

    cleaned = {
        key: _clean_value(value)
        for key, value in record.items()
    }
    if not cleaned.get("flow_id"):
        cleaned["flow_id"] = _generate_flow_id(cleaned)

    if cleaned.get("protocol") is not None:
        cleaned["protocol"] = str(cleaned["protocol"]).upper()

    if cleaned.get("tls_fingerprint") == "":
        cleaned["tls_fingerprint"] = None

    return cleaned

def _generate_flow_id(record: dict) -> str:
    """
    Generate a deterministic identifier for a network flow.

    The ID is derived only from observed flow metadata.
    No network communication or source lookup is performed.
    """

    flow_identity = "|".join(
        str(record.get(field, ""))
        for field in [
            "timestamp",
            "src_ip",
            "src_port",
            "dst_ip",
            "dst_port",
            "protocol",
        ]
    )

    digest = hashlib.sha256(
        flow_identity.encode("utf-8")
    ).hexdigest()

    return f"flow-{digest[:16]}"
def load_flow_csv(file_path: str) -> pd.DataFrame:
    """
    Read-only ingestion of previously collected network-flow data.

    The function:
    1. Loads the CSV.
    2. Checks required fields.
    3. Sanitizes missing values.
    4. Validates every flow using Pydantic.
    5. Returns a normalized DataFrame.

    CYBER-ASTRA never contacts the original source network.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Flow file not found: {file_path}"
        )

    df = pd.read_csv(path)

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    validated_records = []

    for index, row in df.iterrows():

        record = _normalize_record(row.to_dict())

        try:
            flow = TrafficFlow.model_validate(record)

            validated_records.append(
                flow.model_dump(mode="json")
            )

        except Exception as error:

            raise ValueError(
                f"Invalid traffic flow at row {index + 2}: {error}"
            ) from error

    return pd.DataFrame(validated_records)