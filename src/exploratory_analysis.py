"""Exploratory data analysis helpers."""

from __future__ import annotations

import pandas as pd
import numpy as np


def dataset_overview(df: pd.DataFrame, event_col: str | None = None, time_col: str | None = None) -> dict:
    """Return a high-level overview dict for the dataset overview panel."""
    overview = {
        "n_rows": len(df),
        "n_cols": df.shape[1],
        "total_missing": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_cols": df.select_dtypes(include="number").columns.tolist(),
        "categorical_cols": df.select_dtypes(include=["object", "category"]).columns.tolist(),
    }
    if event_col and event_col in df.columns:
        vc = df[event_col].value_counts(dropna=False)
        overview["event_counts"] = vc.to_dict()
    if time_col and time_col in df.columns:
        t = df[time_col].dropna()
        overview["follow_up_median"] = round(t.median(), 2)
        overview["follow_up_range"] = (round(t.min(), 2), round(t.max(), 2))
        if event_col and event_col in df.columns:
            censored = int((df[event_col] == 0).sum())
            overview["censoring_pct"] = round(censored / len(df) * 100, 1)
    return overview


def bivariate_summary(
    df: pd.DataFrame,
    outcome_col: str,
    group_col: str,
    event_value=1,
) -> pd.DataFrame:
    """Cross-tabulation of outcome by group with row percentages."""
    ct = pd.crosstab(df[group_col], df[outcome_col], margins=True)
    pct = pd.crosstab(df[group_col], df[outcome_col], normalize="index") * 100
    pct = pct.round(1)
    return ct, pct
