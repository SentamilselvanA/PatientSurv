"""Rule-based interpretation engine: translates statistical outputs into plain English."""

from __future__ import annotations

import numpy as np


def interpret_test_result(result: dict) -> str:
    """
    Generate a plain-English interpretation from a hypothesis test result dict.
    All statements are derived from computed values; no LLM is used.
    """
    lines = []
    p = result.get("p_value", np.nan)
    alpha = result.get("alpha", 0.05)
    n = result.get("n", 0)
    effect = result.get("effect_size", np.nan)
    effect_label = result.get("effect_label", "Effect size")
    ci = result.get("ci")
    sig = result.get("significant", False)

    # Significance
    if np.isnan(p):
        lines.append("The p-value could not be computed.")
    elif sig:
        lines.append(
            f"The test found statistically significant evidence against the null hypothesis "
            f"(p = {p:.4f} < α = {alpha})."
        )
    else:
        lines.append(
            f"The test did not find statistically significant evidence against the null hypothesis "
            f"(p = {p:.4f} ≥ α = {alpha}). "
            "A non-significant result does not prove the groups are identical."
        )

    # Effect size
    if effect is not None and not np.isnan(effect):
        magnitude = _effect_magnitude(effect_label, effect)
        lines.append(f"{effect_label} = {effect:.3f} ({magnitude} effect).")

    # Confidence interval
    if ci:
        lines.append(
            f"95% confidence interval for the difference: ({ci[0]:.3f}, {ci[1]:.3f}). "
            + ("The interval is wide, indicating imprecision." if abs(ci[1] - ci[0]) > 0.3 else "")
        )

    # Sample size warning
    if n < 30:
        lines.append(
            f"⚠ Small sample size (n = {n}). Results should be interpreted with caution."
        )

    # Existing interpretation from the test function
    existing = result.get("interpretation", "")
    if existing and existing not in " ".join(lines):
        lines.append(existing)

    return " ".join(lines)


def _effect_magnitude(label: str, value: float) -> str:
    label_lower = label.lower()
    if "cohen" in label_lower or "hedges" in label_lower:
        v = abs(value)
        if v < 0.2:
            return "negligible"
        if v < 0.5:
            return "small"
        if v < 0.8:
            return "medium"
        return "large"
    if "cramér" in label_lower or "cramer" in label_lower:
        v = abs(value)
        if v < 0.1:
            return "negligible"
        if v < 0.3:
            return "small"
        if v < 0.5:
            return "moderate"
        return "large"
    if "odds" in label_lower:
        v = abs(np.log(value)) if value > 0 else 0
        if v < 0.2:
            return "negligible"
        if v < 0.5:
            return "small"
        if v < 0.8:
            return "moderate"
        return "large"
    return "unknown magnitude"


def interpret_missing_data(missing_pct: float, col: str) -> str:
    if missing_pct == 0:
        return f"'{col}' has no missing values."
    if missing_pct < 5:
        return f"'{col}' has {missing_pct:.1f}% missing values (low; likely minimal impact)."
    if missing_pct < 20:
        return (
            f"'{col}' has {missing_pct:.1f}% missing values (moderate; "
            "consider whether missingness is random or systematic)."
        )
    return (
        f"'{col}' has {missing_pct:.1f}% missing values (high; "
        "results may be substantially affected by missing data)."
    )


def interpret_km_result(km_info: dict, group_col: str) -> str:
    median = km_info.get("median_survival")
    n = km_info.get("n_subjects", 0)
    n_events = km_info.get("n_events", 0)
    label = km_info.get("label", "")
    if median is None:
        return (
            f"Group '{label}' (n={n}, events={n_events}): "
            "Median survival time was not reached within the observation period."
        )
    return (
        f"Group '{label}' (n={n}, events={n_events}): "
        f"Estimated median survival time is {median:.1f} time units."
    )


def interpret_cox_result(cox_result: dict) -> str:
    if "error" in cox_result:
        return f"Cox model could not be fitted: {cox_result['error']}"
    c_idx = cox_result.get("concordance_index", np.nan)
    n = cox_result.get("n", 0)
    n_ev = cox_result.get("n_events", 0)
    lines = [
        f"Cox proportional hazards model fitted on {n} patients ({n_ev} events).",
        f"Concordance index (C-statistic) = {c_idx:.3f} "
        f"({'good' if c_idx > 0.7 else 'moderate' if c_idx > 0.6 else 'poor'} discrimination).",
        "Hazard ratios represent the multiplicative change in the instantaneous event rate "
        "per unit increase in a covariate, holding other covariates constant. "
        "A hazard ratio is not equivalent to a risk ratio or a survival probability difference.",
    ]
    return " ".join(lines)


def generate_findings_summary(
    outcome_summary: dict,
    test_results: list[dict],
    km_summaries: list[dict] | None = None,
    cox_result: dict | None = None,
) -> str:
    """Assemble a plain-English findings summary from all computed results."""
    parts = []

    # Overall outcome
    p = outcome_summary.get("proportion", np.nan)
    n = outcome_summary.get("n_total", 0)
    n_ev = outcome_summary.get("n_event", 0)
    parts.append(
        f"Overall, {n_ev} of {n} patients ({p:.1%}) experienced the event of interest "
        f"(95% CI: {outcome_summary.get('ci_lower', 0):.1%}–{outcome_summary.get('ci_upper', 0):.1%})."
    )

    # Hypothesis tests
    sig_tests = [r for r in test_results if r.get("significant")]
    nonsig_tests = [r for r in test_results if not r.get("significant")]
    if sig_tests:
        parts.append(
            f"{len(sig_tests)} of {len(test_results)} hypothesis test(s) found statistically "
            "significant associations at the configured significance level."
        )
    else:
        parts.append(
            f"None of the {len(test_results)} hypothesis test(s) found statistically significant "
            "associations at the configured significance level."
        )

    # KM
    if km_summaries:
        for km in km_summaries:
            parts.append(interpret_km_result(km, ""))

    # Cox
    if cox_result and "error" not in cox_result:
        parts.append(interpret_cox_result(cox_result))

    parts.append(
        "These findings are based on observational data. Observed associations do not imply "
        "causation. Differences may reflect confounding, selection bias, or missing data."
    )

    return "\n\n".join(parts)
