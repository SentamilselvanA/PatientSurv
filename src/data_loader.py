"""Data loading: synthetic dataset generation and CSV/Excel ingestion."""

from __future__ import annotations

import io
import logging
from typing import Optional

import numpy as np
import pandas as pd

from config.settings import RANDOM_SEED, SYNTHETIC_N, MAX_UPLOAD_MB

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Synthetic dataset
# ---------------------------------------------------------------------------

SYNTHETIC_SCHEMA = {
    "patient_id":    "Unique patient identifier (string)",
    "age":           "Age at diagnosis in years (numeric)",
    "sex":           "Biological sex: Male / Female (categorical)",
    "stage":         "Disease stage: I / II / III / IV (categorical)",
    "subtype":       "Disease subtype: A / B / C (categorical)",
    "treatment":     "Treatment received: Surgery / Chemo / Radiation / Combined (categorical)",
    "follow_up_months": "Follow-up duration in months (numeric, ≥ 0)",
    "event":         "Event indicator: 1 = death occurred, 0 = censored (binary)",
    "survival_5yr":  "Survived 5 years: 1 = yes, 0 = no (binary)",
    "comorbidity_score": "Comorbidity index 0–4 (numeric)",
    "region":        "Geographic region: North / South / East / West (categorical)",
}


def generate_synthetic_dataset(n: int = SYNTHETIC_N, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """
    Generate a clearly labeled synthetic patient survival dataset.

    Parameters
    ----------
    n : int
        Number of synthetic patient records.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Synthetic dataset with documented schema.

    Notes
    -----
    This dataset is SYNTHETIC and must never be presented as real clinical data.
    It is generated solely for application development and testing.
    """
    rng = np.random.default_rng(seed)

    age = rng.integers(18, 85, size=n).astype(float)
    # Introduce ~3 % missing ages
    age[rng.choice(n, size=int(0.03 * n), replace=False)] = np.nan

    sex = rng.choice(["Male", "Female"], size=n, p=[0.52, 0.48])
    stage = rng.choice(["I", "II", "III", "IV"], size=n, p=[0.25, 0.30, 0.28, 0.17])
    subtype = rng.choice(["A", "B", "C"], size=n, p=[0.40, 0.35, 0.25])
    treatment = rng.choice(
        ["Surgery", "Chemo", "Radiation", "Combined"], size=n, p=[0.30, 0.25, 0.20, 0.25]
    )
    region = rng.choice(["North", "South", "East", "West"], size=n)
    comorbidity = rng.integers(0, 5, size=n).astype(float)

    # Survival time: stage IV patients have shorter follow-up on average
    stage_hazard = {"I": 0.3, "II": 0.5, "III": 0.8, "IV": 1.5}
    base_time = rng.exponential(scale=60, size=n)
    hazard_mult = np.array([stage_hazard[s] for s in stage])
    follow_up = np.clip(base_time / hazard_mult, 0.5, 120).round(1)

    # Event: higher probability for advanced stage and older patients
    event_prob = 0.15 + 0.12 * hazard_mult + 0.003 * np.where(np.isnan(age), 50, age)
    event_prob = np.clip(event_prob, 0.05, 0.95)
    event = rng.binomial(1, event_prob).astype(int)

    # 5-year survival: patients with follow_up >= 60 and event == 0
    survival_5yr = ((follow_up >= 60) & (event == 0)).astype(int)

    # Introduce ~2 % missing follow-up
    follow_up_col = follow_up.astype(float)
    follow_up_col[rng.choice(n, size=int(0.02 * n), replace=False)] = np.nan

    df = pd.DataFrame(
        {
            "patient_id": [f"P{i:05d}" for i in range(1, n + 1)],
            "age": age,
            "sex": sex,
            "stage": stage,
            "subtype": subtype,
            "treatment": treatment,
            "follow_up_months": follow_up_col,
            "event": event,
            "survival_5yr": survival_5yr,
            "comorbidity_score": comorbidity,
            "region": region,
        }
    )

    logger.info("Generated synthetic dataset: %d rows, %d columns", len(df), df.shape[1])
    return df


# ---------------------------------------------------------------------------
# File loading
# ---------------------------------------------------------------------------

def load_csv(source: io.BytesIO | str, **kwargs) -> pd.DataFrame:
    """Load a CSV file from a file path or BytesIO buffer."""
    try:
        df = pd.read_csv(source, **kwargs)
        logger.info("Loaded CSV: %d rows, %d columns", len(df), df.shape[1])
        return df
    except Exception as exc:
        raise ValueError(f"Could not read CSV: {exc}") from exc


def load_excel(source: io.BytesIO | str, sheet_name=0, **kwargs) -> pd.DataFrame:
    """Load an Excel file (.xlsx or .xls) from a file path or BytesIO buffer."""
    try:
        df = pd.read_excel(source, sheet_name=sheet_name, **kwargs)
        logger.info("Loaded Excel: %d rows, %d columns", len(df), df.shape[1])
        return df
    except Exception as exc:
        raise ValueError(f"Could not read Excel: {exc}") from exc


def get_excel_sheet_names(source: io.BytesIO | str) -> list[str]:
    """Return sheet names from an Excel workbook."""
    try:
        xl = pd.ExcelFile(source)
        return xl.sheet_names
    except Exception as exc:
        raise ValueError(f"Could not inspect Excel sheets: {exc}") from exc


def load_file(
    source: io.BytesIO | str,
    filename: str,
    sheet_name=0,
) -> pd.DataFrame:
    """
    Dispatch to the correct loader based on file extension.

    Parameters
    ----------
    source : BytesIO or str
        File content or path.
    filename : str
        Original filename used to determine format.
    sheet_name : int or str
        Sheet selector for Excel files.

    Returns
    -------
    pd.DataFrame
    """
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        return load_csv(source)
    elif ext in ("xlsx", "xls"):
        return load_excel(source, sheet_name=sheet_name)
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Upload a CSV or Excel file.")


def check_file_size(file_bytes: bytes, max_mb: int = MAX_UPLOAD_MB) -> None:
    """Raise ValueError if file exceeds the configured size limit."""
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_mb:
        raise ValueError(
            f"File size {size_mb:.1f} MB exceeds the {max_mb} MB limit."
        )
