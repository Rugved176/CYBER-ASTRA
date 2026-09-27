from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


class DatasetAdapter:
    """
    Base adapter for external cybersecurity datasets.

    Each dataset adapter converts its original columns into the
    common CYBER-ASTRA flow representation.
    """

    dataset_name: str = "unknown"

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)

    def find_csv_files(self) -> list[Path]:
        """Find CSV files recursively inside the dataset directory."""
        if not self.root_dir.exists():
            return []

        return sorted(self.root_dir.rglob("*.csv"))

    def load_csv(self, path: str | Path) -> pd.DataFrame:
        """Load one CSV safely."""
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")

        return pd.read_csv(path, low_memory=False)

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names for easier mapping."""
        result = df.copy()

        result.columns = (
            result.columns
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
            .str.replace("-", "_", regex=False)
        )

        return result

    def add_dataset_metadata(
        self,
        df: pd.DataFrame,
        source_file: Optional[str] = None,
    ) -> pd.DataFrame:
        """Attach dataset provenance."""
        result = df.copy()

        result["dataset_source"] = self.dataset_name

        if source_file is not None:
            result["dataset_file"] = str(source_file)

        return result

    def load(self) -> pd.DataFrame:
        raise NotImplementedError(
            f"{self.__class__.__name__}.load() must be implemented."
        )