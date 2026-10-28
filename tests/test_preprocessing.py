"""Tests for preprocessing module."""

import pytest
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.preprocessing import preprocess, add_age_groups
from src.data_loader import generate_synthetic_dataset


@pytest.fixture
def base_df():
    return generate_synthetic_dataset(n=200, seed=42)


def test_preprocess_removes_duplicates(base_df):
    df_dup = pd.concat([base_df, base_df.iloc[:10]], ignore_index=True)
    df_clean, log = preprocess(df_dup, drop_duplicate_rows=True)
    assert len(df_clean) == len(base_df)


def test_preprocess_removes_negative_time():
    df = pd.DataFrame({
        "time": [-1.0, 5.0, 10.0],
        "event": [1, 0, 1],
        "outcome": [0, 1, 1],
    })
    df_clean, log = preprocess(df, time_col="time", event_col="event",
                               drop_negative_time=True, drop_missing_outcome=False)
    assert (df_clean["time"] >= 0).all()


def test_preprocess_removes_missing_outcome():
    df = pd.DataFrame({
        "time": [1.0, 2.0, 3.0],
        "event": [1, np.nan, 0],
    })
    df_clean, log = preprocess(df, event_col="event", drop_missing_outcome=True)
    assert df_clean["event"].notna().all()


def test_preprocess_preserves_original(base_df):
    original_len = len(base_df)
    preprocess(base_df, drop_duplicate_rows=True)
    assert len(base_df) == original_len  # original not modified


def test_preprocess_log_records_steps(base_df):
    _, log = preprocess(base_df, drop_duplicate_rows=True)
    assert len(log.steps) >= 2


def test_add_age_groups():
    df = pd.DataFrame({"age": [25, 45, 60, 70, 80, np.nan]})
    df_out = add_age_groups(df, "age")
    assert "age_group" in df_out.columns
    assert df_out.loc[df_out["age"].isna(), "age_group"].iloc[0] == "Unknown"


def test_add_age_groups_missing_col():
    df = pd.DataFrame({"x": [1, 2]})
    df_out = add_age_groups(df, "age")
    assert "age_group" not in df_out.columns
