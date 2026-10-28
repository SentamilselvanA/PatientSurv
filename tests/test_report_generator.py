"""Tests for report_generator module."""

import os
import pytest
import pandas as pd
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.report_generator import generate_pdf_report, export_csv


@pytest.fixture
def minimal_report_args(tmp_path):
    return dict(
        output_path=str(tmp_path / "test_report.pdf"),
        dataset_name="Test Dataset",
        dataset_source="Test source",
        dataset_description="A test description.",
        preprocessing_log=pd.DataFrame({"step": ["Original"], "rows_before": [100], "rows_after": [100], "detail": [""]}),
        numeric_summary=pd.DataFrame({"Variable": ["age"], "N": [100], "Mean": [50.0], "Median": [50.0], "SD": [10.0], "IQR": [15.0], "Min": [20.0], "Max": [80.0], "Missing": [0], "Missing %": [0.0]}),
        outcome_summary={"n_total": 100, "n_event": 40, "n_nonevent": 60, "proportion": 0.4, "ci_lower": 0.31, "ci_upper": 0.49},
        test_results=[{
            "test_name": "Chi-Square", "h0": "H0", "h1": "H1",
            "n": 100, "statistic": 4.5, "p_value": 0.034,
            "effect_size": 0.21, "effect_label": "Cramér's V",
            "significant": True, "interpretation": "Significant.",
            "limitations": "Observational.",
        }],
        km_summaries=None,
        cox_result=None,
        findings_text="Overall 40% event rate.",
        limitations_text="Observational data only.",
        reproducibility_text="Seed: 42",
    )


def test_pdf_generated(minimal_report_args):
    path = generate_pdf_report(**minimal_report_args)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 1000


def test_export_csv(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    path = str(tmp_path / "out.csv")
    export_csv(df, path)
    df_back = pd.read_csv(path)
    pd.testing.assert_frame_equal(df, df_back)
