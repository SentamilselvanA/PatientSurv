"""Tests for data_loader module."""

import io
import pytest
import pandas as pd
import numpy as np

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import (
    generate_synthetic_dataset, load_csv, load_excel,
    load_file, check_file_size, SYNTHETIC_SCHEMA
)


def test_synthetic_dataset_shape():
    df = generate_synthetic_dataset(n=100, seed=42)
    assert len(df) == 100
    assert df.shape[1] == len(SYNTHETIC_SCHEMA)


def test_synthetic_dataset_reproducible():
    df1 = generate_synthetic_dataset(n=50, seed=42)
    df2 = generate_synthetic_dataset(n=50, seed=42)
    pd.testing.assert_frame_equal(df1, df2)


def test_synthetic_event_binary():
    df = generate_synthetic_dataset(n=200, seed=1)
    assert set(df["event"].dropna().unique()).issubset({0, 1})


def test_synthetic_follow_up_nonnegative():
    df = generate_synthetic_dataset(n=200, seed=1)
    assert (df["follow_up_months"].dropna() >= 0).all()


def test_load_csv_valid():
    csv_content = b"a,b,c\n1,2,3\n4,5,6\n"
    df = load_csv(io.BytesIO(csv_content))
    assert df.shape == (2, 3)


def test_load_csv_empty_raises():
    with pytest.raises(Exception):
        load_csv(io.BytesIO(b""))


def test_load_file_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported"):
        load_file(io.BytesIO(b"data"), "file.json")


def test_check_file_size_ok():
    check_file_size(b"x" * 1024, max_mb=1)  # 1 KB, limit 1 MB


def test_check_file_size_exceeds():
    with pytest.raises(ValueError, match="exceeds"):
        check_file_size(b"x" * (2 * 1024 * 1024), max_mb=1)


def test_load_excel_valid(tmp_path):
    df_orig = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    path = tmp_path / "test.xlsx"
    df_orig.to_excel(path, index=False)
    df = load_excel(str(path))
    pd.testing.assert_frame_equal(df, df_orig)
