"""Descriptive statistics for numerical and categorical variables."""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats


def numeric_summary(df: pd.DataFrame, cols: list[str] | None = None) -> pd.DataFrame:
    """
    Return mean, median, SD, IQR, min, max, and missing count for numeric columns.

    Parameters
    ----------
    df : pd.DataFrame
    cols : list of str, optional
        Subset of columns; defaults to all numeric columns.

    Returns
    -------
    pd.DataFrame  (one row per variable)
    """
    if cols is None:
        cols = df.select_dtypes(include="number").columns.tolist()
    rows = []
    for col in cols:
        s = df[col].dropna()
        q1, q3 = np.percentile(s, [25, 75]) if len(s) else (np.nan, np.nan)
        rows.append(
            {
                "Variable": col,
                "N": len(s),
                "Missing": int(df[col].isna().sum()),
                "Missing %": round(df[col].isna().mean() * 100, 1),
                "Mean": round(s.mean(), 3) if len(s) else np.nan,
                "Median": round(s.median(), 3) if len(s) else np.nan,
                "SD": round(s.std(), 3) if len(s) else np.nan,
                "IQR": round(q3 - q1, 3) if len(s) else np.nan,
                "Min": round(s.min(), 3) if len(s) else np.nan,
                "Max": round(s.max(), 3) if len(s) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def categorical_summary(df: pd.DataFrame, cols: list[str] | None = None) -> dict[str, pd.DataFrame]:
    """
    Return frequency tables for categorical columns.

    Returns
    -------
    dict mapping column name -> DataFrame with columns [Category, Count, Percent]
    """
    if cols is None:
        cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    result = {}
    for col in cols:
        vc = df[col].value_counts(dropna=False)
        tbl = pd.DataFrame(
            {
                "Category": vc.index.astype(str),
                "Count": vc.values,
                "Percent": (vc.values / len(df) * 100).round(1),
            }
        )
        result[col] = tbl
    return result


def outcome_summary(
    df: pd.DataFrame,
    outcome_col: str,
    event_value: int = 1,
    alpha: float = 0.05,
) -> dict:
    """
    Summarise a binary outcome: counts, proportions, and Wilson confidence interval.

    Parameters
    ----------
    df : pd.DataFrame
    outcome_col : str
    event_value : int
        Value that represents the event of interest.
    alpha : float
        Significance level for the confidence interval.

    Returns
    -------
    dict with keys: n_total, n_event, n_nonevent, proportion, ci_lower, ci_upper
    """
    col = df[outcome_col].dropna()
    n = len(col)
    n_event = int((col == event_value).sum())
    p = n_event / n if n > 0 else np.nan

    # Wilson score interval
    z = stats.norm.ppf(1 - alpha / 2)
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    ci_lo = max(0.0, centre - margin)
    ci_hi = min(1.0, centre + margin)

    return {
        "n_total": n,
        "n_event": n_event,
        "n_nonevent": n - n_event,
        "proportion": round(p, 4),
        "ci_lower": round(ci_lo, 4),
        "ci_upper": round(ci_hi, 4),
    }


def group_outcome_summary(
    df: pd.DataFrame,
    outcome_col: str,
    group_col: str,
    event_value: int = 1,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Return outcome_summary for each level of group_col."""
    rows = []
    for grp, sub in df.groupby(group_col, observed=True):
        s = outcome_summary(sub, outcome_col, event_value, alpha)
        s["group"] = grp
        rows.append(s)
    return pd.DataFrame(rows)[
        ["group", "n_total", "n_event", "n_nonevent", "proportion", "ci_lower", "ci_upper"]
    ]
