"""Tests for survival_analysis module."""

import pytest
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.survival_analysis import (
    fit_kaplan_meier, km_summary, km_by_group,
    log_rank_test, fit_cox
)


@pytest.fixture
def surv_df():
    """Small synthetic survival dataset with known properties."""
    return pd.DataFrame({
        "time":  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                  2, 3, 4, 5, 6, 7, 8, 9, 10, 12],
        "event": [1, 1, 0, 1, 0, 1, 0, 0, 1,  0,
                  1, 0, 1, 0, 1, 0, 1, 0, 0,  1],
        "group": ["A"]*10 + ["B"]*10,
        "age":   [50,55,60,45,70,65,48,52,58,63,
                  40,44,50,55,60,65,70,45,48,52],
    })


def test_km_fit_runs(surv_df):
    kmf = fit_kaplan_meier(surv_df, "time", "event")
    assert kmf is not None


def test_km_survival_starts_at_one(surv_df):
    kmf = fit_kaplan_meier(surv_df, "time", "event")
    sf = kmf.survival_function_
    assert abs(sf.iloc[0, 0] - 1.0) < 1e-9


def test_km_survival_nonincreasing(surv_df):
    kmf = fit_kaplan_meier(surv_df, "time", "event")
    sf = kmf.survival_function_.iloc[:, 0].values
    assert all(sf[i] >= sf[i+1] for i in range(len(sf)-1))


def test_km_summary_keys(surv_df):
    kmf = fit_kaplan_meier(surv_df, "time", "event")
    s = km_summary(kmf)
    assert "n_subjects" in s
    assert "n_events" in s
    assert "median_survival" in s


def test_km_by_group_returns_two(surv_df):
    fitters = km_by_group(surv_df, "time", "event", "group")
    assert len(fitters) == 2
    assert "A" in fitters and "B" in fitters


def test_log_rank_runs(surv_df):
    r = log_rank_test(surv_df, "time", "event", "group")
    assert "p_value" in r
    assert not np.isnan(r["p_value"])


def test_log_rank_single_group():
    df = pd.DataFrame({"time": [1,2,3], "event": [1,0,1], "group": ["A","A","A"]})
    r = log_rank_test(df, "time", "event", "group")
    assert r["significant"] is False


def test_cox_fit_runs(surv_df):
    result = fit_cox(surv_df, "time", "event", ["age"])
    assert "error" not in result or "Insufficient" in result.get("error","")


def test_cox_insufficient_data():
    df = pd.DataFrame({"time": [1,2], "event": [1,0], "age": [50,60]})
    result = fit_cox(df, "time", "event", ["age"])
    assert "error" in result


def test_km_no_events():
    df = pd.DataFrame({"time": [1,2,3,4,5], "event": [0,0,0,0,0]})
    kmf = fit_kaplan_meier(df, "time", "event")
    sf = kmf.survival_function_.iloc[:, 0].values
    assert all(v == 1.0 for v in sf)
