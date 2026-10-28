# Limitations

## Dataset Limitations

- The default dataset is entirely synthetic. It does not represent any real patient population, disease, or clinical setting.
- Synthetic data generation parameters (hazard multipliers, event probabilities) are illustrative and not derived from clinical evidence.
- Real datasets may have additional complexities not captured by this tool.

## Sampling and Selection Bias

- Observational data may over- or under-represent certain patient groups.
- Patients lost to follow-up may differ systematically from those who remained in the study.
- Referral patterns, institutional practices, and data collection methods can introduce selection bias.

## Missing Data

- Missing outcomes and follow-up times are excluded (complete-case analysis).
- If data are not missing completely at random, exclusion may introduce bias.
- No multiple imputation is performed; sensitivity analyses for missing data are not automated.

## Confounding

- All comparisons are unadjusted unless a Cox model is fitted.
- Observed differences between groups may reflect age, disease severity, treatment selection, or other unmeasured variables rather than the grouping variable itself.
- The Cox model adjusts only for included covariates; residual confounding remains possible.

## Censoring Assumptions

- The log-rank test and Kaplan–Meier estimator assume non-informative censoring.
- If patients are censored because they are deteriorating (informative censoring), survival estimates will be biased.
- Competing risks (e.g., death from other causes) are not modelled separately.

## Model Assumptions

- Cox regression assumes proportional hazards. If this assumption is violated, hazard ratios are averages over time and may be misleading.
- Small sample sizes produce wide confidence intervals and unstable estimates.
- Overfitting is possible when many covariates are included relative to the number of events.

## Causal and Clinical Interpretation

- Statistical associations do not imply causation.
- This tool is not a clinical decision support system and must not be used to guide patient care.
- Results should be interpreted by qualified researchers in the context of the full study design.
