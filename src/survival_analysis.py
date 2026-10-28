"""Survival analysis: Kaplan-Meier, log-rank test, and Cox proportional hazards."""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Kaplan-Meier
# ---------------------------------------------------------------------------

def fit_kaplan_meier(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    label: str = "Overall",
    alpha: float = 0.05,
    ci_type: str = "log-log",
) -> KaplanMeierFitter:
    """Fit a Kaplan-Meier estimator and return the fitted object."""
    kmf = KaplanMeierFitter(alpha=alpha, label=label)
    kmf.fit(
        durations=df[time_col],
        event_observed=df[event_col],
        ci_labels=[f"{label}_lower", f"{label}_upper"],
    )
    return kmf


def km_summary(kmf: KaplanMeierFitter, time_points: list[float] | None = None) -> dict:
    """
    Extract key statistics from a fitted KaplanMeierFitter.

    Returns
    -------
    dict with median survival, confidence interval, and survival at time points.
    """
    median = kmf.median_survival_time_
    ci = kmf.confidence_interval_cumulative_density_

    result = {
        "label": kmf._label,
        "n_subjects": int(kmf.event_table["at_risk"].iloc[0]),
        "n_events": int(kmf.event_table["observed"].sum()),
        "median_survival": float(median) if not np.isinf(median) else None,
        "median_ci": _median_ci(kmf),
    }

    if time_points:
        sf = kmf.survival_function_
        estimates = {}
        for t in time_points:
            idx = sf.index[sf.index <= t]
            if len(idx):
                estimates[t] = round(float(sf.loc[idx[-1]].iloc[0]), 4)
            else:
                estimates[t] = None
        result["survival_at_times"] = estimates

    return result


def _median_ci(kmf: KaplanMeierFitter) -> tuple | None:
    """Extract median survival confidence interval from KM fit."""
    try:
        ci_df = kmf.confidence_interval_survival_function_
        cols = ci_df.columns.tolist()
        # Find where upper CI first crosses 0.5
        lo, hi = None, None
        for col in cols:
            s = ci_df[col]
            cross = s[s <= 0.5]
            if len(cross):
                val = float(cross.index[0])
                if lo is None:
                    lo = val
                else:
                    hi = val
        return (lo, hi) if lo is not None else None
    except Exception:
        return None


def km_by_group(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    group_col: str,
    alpha: float = 0.05,
) -> dict[str, KaplanMeierFitter]:
    """Fit a separate KM curve for each group level."""
    fitters = {}
    for grp, sub in df.groupby(group_col, observed=True):
        if len(sub) < 2:
            logger.warning("Group '%s' has < 2 observations; skipping KM.", grp)
            continue
        fitters[str(grp)] = fit_kaplan_meier(sub, time_col, event_col, label=str(grp), alpha=alpha)
    return fitters


# ---------------------------------------------------------------------------
# Log-rank test
# ---------------------------------------------------------------------------

def log_rank_test(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    group_col: str,
    alpha: float = 0.05,
) -> dict:
    """
    Multivariate log-rank test comparing survival curves across groups.

    Returns a result dict compatible with the hypothesis-testing format.
    """
    groups = df[group_col].dropna().unique()
    n_groups = len(groups)

    if n_groups < 2:
        return {
            "test_name": "Log-Rank Test",
            "p_value": np.nan,
            "statistic": np.nan,
            "interpretation": "Fewer than 2 groups available for comparison.",
            "significant": False,
        }

    result = multivariate_logrank_test(
        df[time_col], df[group_col], df[event_col]
    )
    stat = float(result.test_statistic)
    p_val = float(result.p_value)
    sig = p_val < alpha

    interp = (
        f"The log-rank test {'found' if sig else 'did not find'} statistically significant "
        f"evidence of a difference in survival experience across groups of '{group_col}' "
        f"(χ²({n_groups - 1}) = {stat:.3f}, p = {p_val:.4f}). "
        "Note: the log-rank test does not adjust for confounders."
    )

    return {
        "research_question": f"Do survival curves differ across groups of '{group_col}'?",
        "h0": "Survival functions are identical across all groups.",
        "h1": "At least one group has a different survival function.",
        "test_name": "Log-Rank Test",
        "reason": "Standard non-parametric test for comparing Kaplan-Meier curves.",
        "assumptions": "Independent groups; proportional hazards not required; right-censoring.",
        "n": int(df[time_col].notna().sum()),
        "statistic": round(stat, 4),
        "df": n_groups - 1,
        "p_value": round(p_val, 6),
        "alpha": alpha,
        "significant": sig,
        "interpretation": interp,
        "limitations": "Unadjusted; sensitive to non-proportional hazards.",
    }


# ---------------------------------------------------------------------------
# Cox proportional hazards
# ---------------------------------------------------------------------------

def fit_cox(
    df: pd.DataFrame,
    time_col: str,
    event_col: str,
    covariates: list[str],
    alpha: float = 0.05,
) -> dict:
    """
    Fit a Cox proportional hazards model.

    Parameters
    ----------
    df : pd.DataFrame
    time_col, event_col : str
    covariates : list of str
        Columns to include as covariates (categorical columns are dummified).
    alpha : float

    Returns
    -------
    dict with model summary, concordance index, and PH test results.
    """
    required = [time_col, event_col] + covariates
    sub = df[required].dropna()

    if len(sub) < 20:
        return {"error": f"Insufficient complete cases ({len(sub)}) for Cox regression."}

    # Encode categoricals
    sub_enc = pd.get_dummies(sub, columns=[c for c in covariates if sub[c].dtype == object],
                             drop_first=True)

    cph = CoxPHFitter(alpha=alpha)
    try:
        cph.fit(sub_enc, duration_col=time_col, event_col=event_col, show_progress=False)
    except Exception as exc:
        return {"error": f"Cox model failed to converge: {exc}"}

    summary = cph.summary.copy()
    summary = summary[["coef", "exp(coef)", "se(coef)", "z", "p", f"exp(coef) lower {int((1-alpha)*100)}%",
                        f"exp(coef) upper {int((1-alpha)*100)}%"]].round(4)
    summary.columns = ["coef", "HR", "se", "z", "p_value", "HR_lower", "HR_upper"]

    # Proportional hazards test
    try:
        ph_test = cph.check_assumptions(sub_enc, p_value_threshold=alpha, show_plots=False)
    except Exception:
        ph_test = None

    return {
        "model": cph,
        "summary": summary,
        "concordance_index": round(cph.concordance_index_, 4),
        "n": len(sub),
        "n_events": int(sub[event_col].sum()),
        "log_likelihood": round(cph.log_likelihood_, 4),
        "ph_test": ph_test,
        "covariates": covariates,
    }


def cox_summary_table(cox_result: dict) -> pd.DataFrame:
    """Return a formatted Cox model summary table."""
    if "error" in cox_result:
        return pd.DataFrame({"Error": [cox_result["error"]]})
    return cox_result["summary"].reset_index()
