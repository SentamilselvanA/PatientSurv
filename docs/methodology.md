# Methodology

## Study Design

Observational, retrospective analysis of patient survival outcomes. The unit of analysis is the individual patient record. No intervention is assigned; the study examines associations between pre-existing characteristics and outcomes.

## Statistical Assumptions

- Observations are independent.
- Right-censoring is non-informative (censoring is unrelated to the probability of the event).
- For the log-rank test: survival functions are compared over the observed period without assuming proportional hazards.
- For Cox regression: the proportional hazards assumption is assessed using Schoenfeld residuals.

## Hypothesis Definitions

All hypotheses are two-sided unless otherwise stated. The null hypothesis is that no difference exists between groups. The alternative is that a difference exists.

## Test-Selection Logic

| Scenario | Test |
|---|---|
| Binary outcome, 2 groups, adequate counts | Two-proportion z-test |
| Binary outcome, 2 groups, sparse counts | Fisher's exact test |
| Binary outcome, multiple groups | Chi-square test of independence |
| Numeric outcome, 2 groups | Welch's independent-samples t-test |
| Numeric outcome, multiple groups | Kruskal-Wallis H-test |
| Survival curves, multiple groups | Log-rank test |
| Multivariable survival | Cox proportional hazards |

## Survival Analysis Methodology

- **Kaplan–Meier estimator**: non-parametric product-limit estimator of the survival function. Handles right-censored observations correctly.
- **Log-rank test**: non-parametric test comparing survival experience across groups. Does not adjust for confounders.
- **Cox proportional hazards**: semi-parametric regression model. Categorical variables are dummy-coded with the first level as reference. Proportional hazards assumption is assessed.

## Effect Sizes

| Test | Effect size |
|---|---|
| Two-proportion | Odds ratio, absolute risk difference |
| Chi-square | Cramér's V |
| t-test | Cohen's d |
| Kruskal-Wallis | η² (approximate) |
| Cox | Hazard ratio |

## Missing-Data Strategy

- Missing outcomes and follow-up times are excluded from the analytical sample.
- Missing covariates are excluded from complete-case analyses.
- No imputation of survival times or event indicators is performed.
- The impact of missing data is reported in the preprocessing audit log.

## Confidence Intervals

- Proportions: Wilson score interval.
- Mean differences: t-distribution-based interval.
- Hazard ratios: profile likelihood interval (lifelines default).
- Survival function: log-log transformation (Greenwood formula).

## Multiple Testing

When multiple hypothesis tests are conducted, Holm's step-down procedure is applied by default. The Benjamini–Hochberg FDR procedure is available as an alternative. Both raw and adjusted p-values are reported.
