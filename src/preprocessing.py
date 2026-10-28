"""Preprocessing: cleaning, filtering, and audit logging."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class PreprocessingLog:
    """Immutable audit trail of every preprocessing step."""

    steps: list[dict] = field(default_factory=list)

    def record(self, step: str, before: int, after: int, detail: str = "") -> None:
        self.steps.append(
            {"step": step, "rows_before": before, "rows_after": after, "detail": detail}
        )

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.steps)


def preprocess(
    df_raw: pd.DataFrame,
    id_col: Optional[str] = None,
    time_col: Optional[str] = None,
    event_col: Optional[str] = None,
    age_col: Optional[str] = None,
    drop_duplicate_rows: bool = True,
    drop_missing_outcome: bool = True,
    drop_negative_time: bool = True,
    outcome_col: Optional[str] = None,
) -> tuple[pd.DataFrame, PreprocessingLog]:
    """
    Apply documented preprocessing steps and return a clean copy with an audit log.

    The original dataframe is never modified in place.

    Parameters
    ----------
    df_raw : pd.DataFrame
        Raw uploaded dataset.
    id_col, time_col, event_col, age_col, outcome_col : str, optional
        Column role assignments.
    drop_duplicate_rows : bool
        Remove exact duplicate rows.
    drop_missing_outcome : bool
        Remove rows where the primary outcome is missing.
    drop_negative_time : bool
        Remove rows with negative follow-up time.

    Returns
    -------
    (cleaned_df, PreprocessingLog)
    """
    df = df_raw.copy()
    log = PreprocessingLog()
    log.record("Original dataset", len(df), len(df), f"{df.shape[1]} columns")

    # Remove exact duplicate rows
    if drop_duplicate_rows:
        before = len(df)
        df = df.drop_duplicates()
        log.record("Remove duplicate rows", before, len(df), f"Removed {before - len(df)}")

    # Remove duplicate IDs (keep first)
    if id_col and id_col in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=[id_col], keep="first")
        log.record(
            "Remove duplicate IDs",
            before,
            len(df),
            f"Kept first occurrence; removed {before - len(df)}",
        )

    # Remove rows with negative follow-up time
    if drop_negative_time and time_col and time_col in df.columns:
        before = len(df)
        df = df[df[time_col].isna() | (df[time_col] >= 0)]
        log.record(
            "Remove negative follow-up time",
            before,
            len(df),
            f"Removed {before - len(df)}",
        )

    # Remove rows missing the primary outcome
    primary = outcome_col or event_col
    if drop_missing_outcome and primary and primary in df.columns:
        before = len(df)
        df = df[df[primary].notna()]
        log.record(
            f"Remove missing outcome ('{primary}')",
            before,
            len(df),
            f"Removed {before - len(df)}",
        )

    # Remove rows missing follow-up time (required for survival analysis)
    if time_col and time_col in df.columns:
        before = len(df)
        df = df[df[time_col].notna()]
        log.record(
            f"Remove missing follow-up time ('{time_col}')",
            before,
            len(df),
            f"Removed {before - len(df)}",
        )

    # Standardise categorical labels: strip whitespace
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        df[col] = df[col].str.strip()

    log.record("Final analytical sample", len(df), len(df), "")
    logger.info("Preprocessing complete: %d rows retained", len(df))
    return df, log


def add_age_groups(
    df: pd.DataFrame,
    age_col: str,
    bins: list[int] | None = None,
    labels: list[str] | None = None,
) -> pd.DataFrame:
    """Add an 'age_group' column based on configurable bins."""
    if age_col not in df.columns:
        return df
    bins = bins or [0, 40, 55, 65, 75, 200]
    labels = labels or ["<40", "40–54", "55–64", "65–74", "75+"]
    df = df.copy()
    df["age_group"] = pd.cut(
        df[age_col], bins=bins, labels=labels, right=False
    ).astype(str)
    df.loc[df[age_col].isna(), "age_group"] = "Unknown"
    return df
