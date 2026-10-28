"""Hypothesis testing: proportions, chi-square, t-tests, and multiple-testing correction."""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.multitest import multipletests

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

def _result(
    research_question: str,
    h0: str,
    h1: str,
    test_name: str,
    reason: str,
    assumptions: str,
    n: int,
    statistic: float,
    df_val,
    p_value: float,
    alpha: float,
    effect_size: float | None,
    effect_label: str,
    ci: tuple | None,
    interpretation: str,
    limitations: str,
    extra: dict | None = None,
) -> dict:
    significant = p_value < alpha if not np.isnan(p_value) else False
    return {
        "research_question": research_question,
        "h0": h0,
        "h1": h1,
        "test_name": test_name,
        "reason": reason,
        "assumptions": assumptions,
        "n": n,
        "statistic": round(statistic, 4) if not np.isnan(statistic) else np.nan,
        "df": df_val,
        "p_value": round(p_value, 6) if not np.isnan(p_value) else np.nan,
        "alpha": alpha,
        "significant": significant,
        "effect_size": round(effect_size, 4) if effect_size is not None and not np.isnan(effect_size) else np.nan,
        "effect_label": effect_label,
        "ci": (round(ci[0], 4), round(ci[1], 4)) if ci else None,
        "interpretation": interpretation,
        "limitations": limitations,
        **(extra or {}),
    }


# ---------------------------------------------------------------------------
# Two-proportion test
# ---------------------------------------------------------------------------

def two_proportion_test(
    df: pd.DataFrame,
    outcome_col: str,
    group_col: str,
    group_a: str,
    group_b: str,
    event_value=1,
    alpha: float = 0.05,
) -> dict:
    """
    Compare event proportions between two independent groups.

    Uses a two-proportion z-test when expected counts are adequate,
    otherwise Fisher's exact test.
    """
    sub_a = df[df[group_col] == group_a][outcome_col].dropna()
    sub_b = df[df[group_col] == group_b][outcome_col].dropna()
    n_a, n_b = len(sub_a), len(sub_b)
    k_a = int((sub_a == event_value).sum())
    k_b = int((sub_b == event_value).sum())
    p_a = k_a / n_a if n_a else np.nan
    p_b = k_b / n_b if n_b else np.nan

    # Decide test: use Fisher when any expected cell < 5
    table = np.array([[k_a, n_a - k_a], [k_b, n_b - k_b]])
    expected = stats.contingency.expected_freq(table)
    use_fisher = (expected < 5).any()

    if use_fisher:
        stat, p_val = stats.fisher_exact(table)
        test_name = "Fisher's Exact Test"
        reason = "Expected cell count < 5; asymptotic z-test assumptions not met."
        stat_label = "Odds Ratio"
        effect_size = stat
        effect_label = "Odds Ratio"
    else:
        stat, p_val = proportions_ztest([k_a, k_b], [n_a, n_b])
        test_name = "Two-Proportion Z-Test"
        reason = "Expected cell counts ≥ 5; asymptotic approximation appropriate."
        stat_label = "Z"
        # Odds ratio as effect size
        effect_size = (k_a / (n_a - k_a)) / (k_b / (n_b - k_b)) if (n_a - k_a) and (n_b - k_b) else np.nan
        effect_label = "Odds Ratio"

    # Risk difference and CI
    rd = p_a - p_b
    ci_a = proportion_confint(k_a, n_a, alpha=alpha, method="wilson")
    ci_b = proportion_confint(k_b, n_b, alpha=alpha, method="wilson")

    interp = _interpret_proportion(p_a, p_b, group_a, group_b, p_val, alpha, rd, effect_size, use_fisher)

    return _result(
        research_question=f"Do event proportions differ between '{group_a}' and '{group_b}'?",
        h0=f"The proportion of events is equal in '{group_a}' and '{group_b}'.",
        h1=f"The proportion of events differs between '{group_a}' and '{group_b}'.",
        test_name=test_name,
        reason=reason,
        assumptions="Independent observations; binary outcome; adequate sample sizes for z-test.",
        n=n_a + n_b,
        statistic=stat,
        df_val=None,
        p_value=p_val,
        alpha=alpha,
        effect_size=effect_size,
        effect_label=effect_label,
        ci=(rd - 1.96 * np.sqrt(p_a*(1-p_a)/n_a + p_b*(1-p_b)/n_b),
            rd + 1.96 * np.sqrt(p_a*(1-p_a)/n_a + p_b*(1-p_b)/n_b)) if n_a and n_b else None,
        interpretation=interp,
        limitations="Observational data; unadjusted comparison; confounders not controlled.",
        extra={
            "group_a": group_a, "p_a": round(p_a, 4), "n_a": n_a, "k_a": k_a,
            "group_b": group_b, "p_b": round(p_b, 4), "n_b": n_b, "k_b": k_b,
            "risk_difference": round(rd, 4),
            "ci_a": (round(ci_a[0], 4), round(ci_a[1], 4)),
            "ci_b": (round(ci_b[0], 4), round(ci_b[1], 4)),
        },
    )


def _interpret_proportion(p_a, p_b, g_a, g_b, p_val, alpha, rd, or_val, fisher):
    sig = p_val < alpha
    direction = "higher" if rd > 0 else "lower"
    test = "Fisher's exact test" if fisher else "two-proportion z-test"
    if sig:
        return (
            f"The {test} found statistically significant evidence (p = {p_val:.4f}) "
            f"that the event proportion in '{g_a}' ({p_a:.1%}) is {direction} than in "
            f"'{g_b}' ({p_b:.1%}). The absolute risk difference is {abs(rd):.1%}. "
            f"The odds ratio is {or_val:.2f}. This is an unadjusted observational comparison."
        )
    return (
        f"The {test} did not find statistically significant evidence (p = {p_val:.4f}) "
        f"of a difference in event proportions between '{g_a}' ({p_a:.1%}) and "
        f"'{g_b}' ({p_b:.1%}). This does not prove the groups are identical."
    )


# ---------------------------------------------------------------------------
# Chi-square / Fisher for multi-group
# ---------------------------------------------------------------------------

def chi_square_test(
    df: pd.DataFrame,
    outcome_col: str,
    group_col: str,
    alpha: float = 0.05,
) -> dict:
    """Chi-square test of independence between a grouping variable and a binary outcome."""
    ct = pd.crosstab(df[group_col], df[outcome_col])
    n = int(ct.values.sum())
    expected = stats.contingency.expected_freq(ct.values)
    use_exact = (expected < 5).any()

    if use_exact:
        stat, p_val, dof, _ = stats.chi2_contingency(ct.values, correction=False)
        test_name = "Chi-Square (Monte Carlo recommended; sparse cells present)"
        reason = "Some expected counts < 5; interpret with caution."
    else:
        stat, p_val, dof, _ = stats.chi2_contingency(ct.values)
        test_name = "Pearson Chi-Square Test of Independence"
        reason = "All expected cell counts ≥ 5; asymptotic approximation appropriate."

    # Cramér's V
    k = min(ct.shape)
    cramers_v = np.sqrt(stat / (n * (k - 1))) if n and k > 1 else np.nan

    sig = p_val < alpha
    interp = (
        f"{'Statistically significant' if sig else 'No statistically significant'} association "
        f"found between '{group_col}' and '{outcome_col}' "
        f"(χ²({dof}) = {stat:.3f}, p = {p_val:.4f}). "
        f"Cramér's V = {cramers_v:.3f} ({'small' if cramers_v < 0.1 else 'moderate' if cramers_v < 0.3 else 'large'} effect)."
    )

    return _result(
        research_question=f"Is '{group_col}' associated with '{outcome_col}'?",
        h0=f"'{group_col}' and '{outcome_col}' are independent.",
        h1=f"'{group_col}' and '{outcome_col}' are not independent.",
        test_name=test_name,
        reason=reason,
        assumptions="Independent observations; adequate expected cell counts for chi-square.",
        n=n,
        statistic=stat,
        df_val=dof,
        p_value=p_val,
        alpha=alpha,
        effect_size=cramers_v,
        effect_label="Cramér's V",
        ci=None,
        interpretation=interp,
        limitations="Unadjusted; does not control for confounders.",
        extra={"contingency_table": ct.to_dict()},
    )


# ---------------------------------------------------------------------------
# Two-sample t-test / Mann-Whitney
# ---------------------------------------------------------------------------

def two_group_numeric_test(
    df: pd.DataFrame,
    numeric_col: str,
    group_col: str,
    group_a: str,
    group_b: str,
    alpha: float = 0.05,
) -> dict:
    """Welch's t-test for two independent groups on a numeric variable."""
    a = df[df[group_col] == group_a][numeric_col].dropna()
    b = df[df[group_col] == group_b][numeric_col].dropna()
    n_a, n_b = len(a), len(b)

    stat, p_val = stats.ttest_ind(a, b, equal_var=False)
    dof = (a.var()/n_a + b.var()/n_b)**2 / (
        (a.var()/n_a)**2/(n_a-1) + (b.var()/n_b)**2/(n_b-1)
    ) if n_a > 1 and n_b > 1 else np.nan

    # Cohen's d
    pooled_sd = np.sqrt((a.std()**2 + b.std()**2) / 2)
    cohens_d = (a.mean() - b.mean()) / pooled_sd if pooled_sd else np.nan

    mean_diff = a.mean() - b.mean()
    se_diff = np.sqrt(a.var()/n_a + b.var()/n_b)
    t_crit = stats.t.ppf(1 - alpha/2, df=dof) if not np.isnan(dof) else 1.96
    ci = (mean_diff - t_crit * se_diff, mean_diff + t_crit * se_diff)

    sig = p_val < alpha
    interp = (
        f"{'Statistically significant' if sig else 'No statistically significant'} difference "
        f"in mean '{numeric_col}' between '{group_a}' (mean={a.mean():.2f}) and "
        f"'{group_b}' (mean={b.mean():.2f}) "
        f"(Welch's t({dof:.1f}) = {stat:.3f}, p = {p_val:.4f}). "
        f"Cohen's d = {cohens_d:.3f}."
    )

    return _result(
        research_question=f"Does mean '{numeric_col}' differ between '{group_a}' and '{group_b}'?",
        h0=f"Mean '{numeric_col}' is equal in '{group_a}' and '{group_b}'.",
        h1=f"Mean '{numeric_col}' differs between '{group_a}' and '{group_b}'.",
        test_name="Welch's Independent-Samples t-Test",
        reason="Welch's t-test does not assume equal variances; robust for unequal group sizes.",
        assumptions="Independent observations; approximately normal distributions or large samples.",
        n=n_a + n_b,
        statistic=stat,
        df_val=round(dof, 1) if not np.isnan(dof) else None,
        p_value=p_val,
        alpha=alpha,
        effect_size=cohens_d,
        effect_label="Cohen's d",
        ci=ci,
        interpretation=interp,
        limitations="Unadjusted comparison; normality assumed.",
        extra={"mean_a": round(a.mean(), 3), "mean_b": round(b.mean(), 3),
               "sd_a": round(a.std(), 3), "sd_b": round(b.std(), 3)},
    )


def kruskal_wallis_test(
    df: pd.DataFrame,
    numeric_col: str,
    group_col: str,
    alpha: float = 0.05,
) -> dict:
    """Kruskal-Wallis H-test for comparing a numeric variable across multiple groups."""
    groups = [g[numeric_col].dropna().values for _, g in df.groupby(group_col, observed=True)]
    groups = [g for g in groups if len(g) > 0]
    n = sum(len(g) for g in groups)

    if len(groups) < 2:
        return _result(
            "Kruskal-Wallis", "", "", "Kruskal-Wallis", "", "", n,
            np.nan, None, np.nan, alpha, np.nan, "η²", None,
            "Insufficient groups.", "", {}
        )

    stat, p_val = stats.kruskal(*groups)
    # Eta-squared approximation
    k = len(groups)
    eta2 = (stat - k + 1) / (n - k) if n > k else np.nan

    sig = p_val < alpha
    interp = (
        f"{'Statistically significant' if sig else 'No statistically significant'} difference "
        f"in '{numeric_col}' across groups of '{group_col}' "
        f"(H = {stat:.3f}, p = {p_val:.4f}). η² ≈ {eta2:.3f}."
    )

    return _result(
        research_question=f"Does '{numeric_col}' differ across levels of '{group_col}'?",
        h0=f"The distribution of '{numeric_col}' is identical across all groups.",
        h1=f"At least one group differs in '{numeric_col}'.",
        test_name="Kruskal-Wallis H-Test",
        reason="Non-parametric alternative to one-way ANOVA; does not assume normality.",
        assumptions="Independent observations; ordinal or continuous outcome.",
        n=n,
        statistic=stat,
        df_val=k - 1,
        p_value=p_val,
        alpha=alpha,
        effect_size=eta2,
        effect_label="η² (approx.)",
        ci=None,
        interpretation=interp,
        limitations="Does not identify which specific groups differ; post-hoc tests needed.",
    )


# ---------------------------------------------------------------------------
# Multiple-testing correction
# ---------------------------------------------------------------------------

def apply_multiple_testing_correction(
    results: list[dict],
    method: str = "holm",
    alpha: float = 0.05,
) -> list[dict]:
    """
    Apply multiple-testing correction to a list of test result dicts.

    Parameters
    ----------
    results : list of dict
        Each dict must contain a 'p_value' key.
    method : str
        'holm' or 'fdr_bh'.
    alpha : float

    Returns
    -------
    list of dict with added 'p_adjusted' and 'significant_adjusted' keys.
    """
    p_vals = [r["p_value"] for r in results]
    reject, p_adj, _, _ = multipletests(p_vals, alpha=alpha, method=method)
    for r, pa, rej in zip(results, p_adj, reject):
        r["p_adjusted"] = round(float(pa), 6)
        r["significant_adjusted"] = bool(rej)
    return results
