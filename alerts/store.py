import json
import os
import tempfile
from pathlib import Path
from datetime import datetime

from alerts.schema import ThreatAlert


ALERT_FILE = Path("data/alerts.json")


def _atomic_write(data):
    """Safely write the alert database without partial files."""

    ALERT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_file = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=ALERT_FILE.parent,
            suffix=".tmp"
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False
            )

            file.flush()
            os.fsync(file.fileno())

            temp_file = file.name

        os.replace(temp_file, ALERT_FILE)

    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


def save_alerts(alerts):
    """Validate and atomically save all alerts."""

    validated_alerts = []

    for alert in alerts:
        validated = ThreatAlert.model_validate(alert)

        validated_alerts.append(
            validated.model_dump(mode="json")
        )

    payload = {
        "generated_at": datetime.now().isoformat(),
        "alert_count": len(validated_alerts),
        "alerts": validated_alerts
    }

    _atomic_write(payload)


def load_alerts():
    """Load the CYBER-ASTRA alert database."""

    if not ALERT_FILE.exists():
        return {
            "generated_at": None,
            "alert_count": 0,
            "alerts": []
        }

    with open(
        ALERT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def add_alert(alert):
    """Validate and append one alert."""

    data = load_alerts()

    validated = ThreatAlert.model_validate(alert)

    data["alerts"].append(
        validated.model_dump(mode="json")
    )

    data["alert_count"] = len(data["alerts"])
    data["generated_at"] = datetime.now().isoformat()

    _atomic_write(data)


def clear_alerts():
    """Clear the alert database safely."""

    payload = {
        "generated_at": datetime.now().isoformat(),
        "alert_count": 0,
        "alerts": []
    }

    _atomic_write(payload)