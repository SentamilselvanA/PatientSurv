"""Data validation: structural checks, type checks, and quality warnings."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    """Collects all validation findings for a dataset."""

    row_count: int = 0
    col_count: int = 0
    duplicate_rows: int = 0
    duplicate_id_count: int = 0
    missing_per_column: dict = field(default_factory=dict)
    invalid_records: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def to_dict(self) -> dict:
        return {
            "row_count": self.row_count,
            "col_count": self.col_count,
            "duplicate_rows": self.duplicate_rows,
            "duplicate_id_count": self.duplicate_id_count,
            "missing_per_column": self.missing_per_column,
            "invalid_records": self.invalid_records,
            "warnings": self.warnings,
            "errors": self.errors,
        }


def validate_dataset(
    df: pd.DataFrame,
    id_col: Optional[str] = None,
    time_col: Optional[str] = None,
    event_col: Optional[str] = None,
    age_col: Optional[str] = None,
    event_values: tuple = (0, 1),
) -> ValidationReport:
    """
    Run structural and domain validation on a dataset.

    Parameters
    ----------
    df : pd.DataFrame
    id_col : str, optional
        Column containing patient identifiers.
    time_col : str, optional
        Column containing follow-up duration.
    event_col : str, optional
        Column containing event indicator.
    age_col : str, optional
        Column containing patient age.
    event_values : tuple
        Expected (censored_value, event_value).

    Returns
    -------
    ValidationReport
    """
    report = ValidationReport()
    report.row_count = len(df)
    report.col_count = df.shape[1]

    # Duplicate column names
    dup_cols = df.columns[df.columns.duplicated()].tolist()
    if dup_cols:
        report.errors.append(f"Duplicate column names detected: {dup_cols}")

    # Duplicate rows
    report.duplicate_rows = int(df.duplicated().sum())
    if report.duplicate_rows:
        report.warnings.append(
            f"{report.duplicate_rows} exact duplicate rows detected."
        )

    # Duplicate IDs
    if id_col and id_col in df.columns:
        dup_ids = int(df[id_col].duplicated().sum())
        report.duplicate_id_count = dup_ids
        if dup_ids:
            report.warnings.append(
                f"{dup_ids} duplicate values in identifier column '{id_col}'."
            )

    # Missing values per column
    missing = df.isnull().sum()
    report.missing_per_column = {
        col: {"count": int(missing[col]), "pct": round(missing[col] / len(df) * 100, 2)}
        for col in df.columns
    }

    # Constant or entirely missing columns
    for col in df.columns:
        if df[col].isnull().all():
            report.errors.append(f"Column '{col}' is entirely missing.")
        elif df[col].nunique(dropna=True) <= 1:
            report.warnings.append(f"Column '{col}' has only one unique value (constant).")

    # Follow-up time validation
    if time_col and time_col in df.columns:
        neg = (df[time_col] < 0).sum()
        if neg:
            report.invalid_records.append(
                f"{neg} records have negative follow-up time in '{time_col}'."
            )
        zero_event = None
        if event_col and event_col in df.columns:
            zero_event = int(
                ((df[time_col] == 0) & (df[event_col] == event_values[1])).sum()
            )
            if zero_event:
                report.warnings.append(
                    f"{zero_event} records have follow-up time = 0 with event = 1."
                )

    # Event encoding validation
    if event_col and event_col in df.columns:
        valid_vals = set(event_values)
        actual_vals = set(df[event_col].dropna().unique())
        unexpected = actual_vals - valid_vals
        if unexpected:
            report.warnings.append(
                f"Unexpected values in event column '{event_col}': {unexpected}. "
                f"Expected {valid_vals}."
            )

    # Age validation
    if age_col and age_col in df.columns:
        numeric_age = pd.to_numeric(df[age_col], errors="coerce")
        invalid_age = int((numeric_age < 0).sum() + (numeric_age > 130).sum())
        if invalid_age:
            report.invalid_records.append(
                f"{invalid_age} records have implausible age values in '{age_col}'."
            )

    logger.info(
        "Validation complete: %d warnings, %d errors",
        len(report.warnings),
        len(report.errors),
    )
    return report


def check_required_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    """Return list of required columns that are absent from the dataframe."""
    return [c for c in required if c not in df.columns]
