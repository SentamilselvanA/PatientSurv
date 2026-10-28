"""Tests for hypothesis_testing module."""

import pytest
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.hypothesis_testing import (
    two_proportion_test, chi_square_test, two_group_numeric_test,
    kruskal_wallis_test, apply_multiple_testing_correction
)


@pytest.fixture
def prop_df():
    """Known proportions: group A 80/100 events, group B 40/100 events."""
    rng = np.random.default_rng(0)
    a = pd.DataFrame({"group": "A", "event": [1]*80 + [0]*20})
    b = pd.DataFrame({"group": "B", "event": [1]*40 + [0]*60})
    return pd.concat([a, b], ignore_index=True)


def test_two_proportion_significant(prop_df):
    r = two_proportion_test(prop_df, "event", "group", "A", "B", event_value=1)
    assert r["significant"] == True
    assert r["p_value"] < 0.05


def test_two_proportion_effect_size(prop_df):
    r = two_proportion_test(prop_df, "event", "group", "A", "B", event_value=1)
    assert not np.isnan(r["effect_size"])


def test_two_proportion_risk_difference(prop_df):
    r = two_proportion_test(prop_df, "event", "group", "A", "B", event_value=1)
    assert abs(r["risk_difference"] - 0.40) < 0.01


def test_chi_square_significant(prop_df):
    r = chi_square_test(prop_df, "event", "group")
    assert r["significant"] == True
    assert r["p_value"] < 0.05


def test_chi_square_cramers_v(prop_df):
    r = chi_square_test(prop_df, "event", "group")
    assert 0 <= r["effect_size"] <= 1


def test_welch_ttest_known():
    rng = np.random.default_rng(1)
    df = pd.DataFrame({
        "value": np.concatenate([rng.normal(10, 1, 100), rng.normal(12, 1, 100)]),
        "group": ["A"]*100 + ["B"]*100,
    })
    r = two_group_numeric_test(df, "value", "group", "A", "B")
    assert r["significant"] == True
    assert r["p_value"] < 0.05


def test_kruskal_wallis_three_groups():
    rng = np.random.default_rng(2)
    df = pd.DataFrame({
        "value": np.concatenate([rng.normal(5,1,50), rng.normal(10,1,50), rng.normal(15,1,50)]),
        "group": ["A"]*50 + ["B"]*50 + ["C"]*50,
    })
    r = kruskal_wallis_test(df, "value", "group")
    assert r["significant"] == True


def test_multiple_testing_correction():
    results = [
        {"p_value": 0.001, "significant": True},
        {"p_value": 0.04,  "significant": True},
        {"p_value": 0.60,  "significant": False},
    ]
    corrected = apply_multiple_testing_correction(results, method="holm")
    assert all("p_adjusted" in r for r in corrected)
    # After Holm correction, p=0.60 should remain non-significant
    assert corrected[2]["significant_adjusted"] == False


def test_fisher_exact_sparse():
    """Sparse table should trigger Fisher's exact test."""
    df = pd.DataFrame({
        "group": ["A"]*5 + ["B"]*5,
        "event": [1,1,1,0,0, 0,0,0,0,1],
    })
    r = two_proportion_test(df, "event", "group", "A", "B")
    assert "Fisher" in r["test_name"]
