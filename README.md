# Comparative Statistical Analysis of Patient Survival Rates

A complete, production-grade, reproducible data science application for investigating differences in patient survival outcomes across demographic and clinical groups.

---

## Problem Statement

Patient survival outcomes vary significantly across demographic, clinical, and treatment cohorts. Quantifying these differences rigorously requires appropriate statistical methods, transparent data handling, robust multivariable adjustments, and honest uncertainty reporting. 

This application provides an end-to-end clinical biostatistics pipeline—from raw data ingestion, validation, and exploratory data analysis through hypothesis testing, time-to-event survival modeling, and publication-ready PDF reports.

---

## Core Objectives

- **Data Ingestion & Integrity**: Ingest patient cohorts from CSV and Excel files with automated schema validation, duplicate detection, and audit logging.
- **Interactive Exploration**: Interactively analyze patient demographics, clinical characteristics, and survival distributions.
- **Statistical Testing**: Rigorously compare survival and clinical metrics across groups using parametric and non-parametric hypothesis tests with effect sizes and multiple-testing corrections.
- **Time-to-Event Modeling**: Estimate survival probabilities over time using Kaplan–Meier curves, log-rank tests, numbers-at-risk tables, and Cox proportional hazards regression.
- **Automated Interpretation**: Provide plain-English clinical interpretations alongside p-values and confidence intervals.
- **Audit & Reproducibility**: Guarantee reproducibility via tracked seeds, session parameters, and downloadable PDF/CSV artifacts.

---

## Key Features

| Category | Feature | Description |
|---|---|---|
| **UI & Experience** | **Sticky Glassmorphic Navbar** | Responsive top navigation bar with brand identity, icon pills, active status highlighting, and zero text truncation. |
| | **Dark & Light Mode** | Seamless one-click theme switcher with custom color schemes and auto-adapting Plotly visualization templates (`plotly_white` / `plotly_dark`). |
| | **Card-Based Layout** | Native bordered card system with smooth hover animations, crisp iconography, and responsive grid alignment. |
| **Data Ingestion** | **File Uploader** | Drag-and-drop CSV, XLSX, and XLS support with multi-sheet selection and file size guards (up to 50 MB). |
| | **Synthetic Cohort Generator** | Pre-loaded 1,000-patient synthetic clinical dataset generated using fixed seeds for rapid testing and demonstration. |
| | **Schema & Column Mapping** | Interactive column mapper linking custom datasets to analytical roles (`id`, `age`, `sex`, `stage`, `time`, `event`, `outcome`). |
| | **Data Quality Validation** | Automated detection of duplicate IDs, missing values, impossible values (e.g., negative follow-up time), and encoding discrepancies. |
| | **Preprocessing Audit Log** | Detailed log tracking of rows removed, type casting, and feature engineering, downloadable as CSV. |
| **Exploratory Analysis** | **Cohort KPI Metrics** | Live summary cards tracking total cohort size, observed events, censored records, event rates, median age, and follow-up duration. |
| | **Cohort Filters** | Dynamic filtering by age range, biological sex, disease stage, subtype, treatment arm, and region. |
| | **Descriptive Statistics** | Complete parametric and non-parametric summaries (mean, std, median, IQR, skewness, missing counts). |
| | **Interactive Visualizations** | Plotly-powered histograms with KDE, box plots with outlier detection, bar charts, and missing value heatmaps. |
| | **Correlation Analysis** | Interactive correlation matrix heatmap for numeric clinical variables. |
| | **Group Outcome Breakdowns** | Proportional outcome breakdowns by clinical groupings with Wilson score intervals. |
| **Hypothesis Testing** | **Two-Proportion Z-Test** | Compares binary outcome rates between two patient groups with risk difference, odds ratios, and 95% Wilson CIs. |
| | **Chi-Square Test of Independence** | Evaluates associations between categorical grouping variables and multi-category clinical outcomes with Cramér's V. |
| | **Welch's Two-Sample t-Test** | Robust comparison of numeric variables between two independent groups without assuming equal variances (Cohen's d). |
| | **Kruskal–Wallis H-Test** | Non-parametric one-way ANOVA alternative for comparing numeric distributions across multiple groups (Eta-squared $\eta^2$). |
| | **Multiple-Testing Correction** | Step-down Holm procedure and Benjamini–Hochberg False Discovery Rate (FDR) adjustments. |
| | **Interpretation Engine** | Context-aware, rule-based clinical interpretations explaining statistical significance and practical implications. |
| **Survival Analysis** | **Kaplan–Meier Estimation** | Non-parametric survival function estimation with confidence bands and median survival time calculations. |
| | **Numbers-at-Risk Table** | Aligned patient count at risk over designated time intervals across the follow-up window. |
| | **Log-Rank Test** | Hypothesis testing comparing survival distributions across stratified groups (e.g., stages, treatments, age groups). |
| | **Cox Proportional Hazards** | Multivariable semi-parametric survival regression modeling hazard ratios (HR), 95% profile likelihood CIs, p-values, and Harrell's C-index. |
| | **Hazard Ratio Forest Plot** | Visual log-scale forest plot depicting hazard ratios and confidence intervals across covariates. |
| **Reporting & Export** | **Executive Findings Summary** | Auto-synthesized research summary synthesizing findings across all completed tests and models. |
| | **Publication-Ready PDF Report** | Comprehensive ReportLab PDF generator containing executive summaries, clinical findings, tables, limitations, and provenance metadata. |
| | **CSV Data Exports** | One-click export for the processed analytical dataset, statistical test results, and Cox regression tables. |
| | **Reproducibility Record** | Complete execution metadata: Python runtime, dependency versions, random seed, and parameter configurations. |

---

## Technology Stack

- **Application Framework**: [Streamlit](https://streamlit.io/) (1.63+)
- **Data Engineering**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Statistical Testing**: [SciPy](https://scipy.org/), [Statsmodels](https://www.statsmodels.org/)
- **Survival Analysis**: [Lifelines](https://lifelines.readthedocs.io/)
- **Data Visualization**: [Plotly](https://plotly.com/python/)
- **Report Generation**: [ReportLab](https://www.reportlab.com/)
- **Excel Support**: [OpenPyXL](https://openpyxl.readthedocs.io/), [XLRD](https://xlrd.readthedocs.io/)
- **Quality Assurance**: [Pytest](https://docs.pytest.org/), [Pytest-Cov](https://pytest-cov.readthedocs.io/)

---

## Project Structure

```
ds-project/
├── app.py                         # Streamlit application entry point & page routing
├── requirements.txt               # Pinned project dependencies
├── README.md                      # Project documentation
├── .gitignore                     # Git ignore rules
├── config/
│   └── settings.py                # Global settings, alpha defaults, paths, seeds
├── data/
│   ├── README.md                  # Dataset documentation
│   └── sample/                    # Sample clinical datasets
├── src/
│   ├── data_loader.py             # File ingestion (CSV/Excel) & synthetic cohort generator
│   ├── data_validation.py         # Structural, domain, and constraint validations
│   ├── preprocessing.py           # Missing data handling, deduplication, audit log
│   ├── descriptive_statistics.py  # Numeric and categorical summary statistics
│   ├── exploratory_analysis.py    # Dataset overview and bivariate cross-tabulations
│   ├── hypothesis_testing.py      # Parametric & non-parametric tests, corrections, effect sizes
│   ├── survival_analysis.py       # Kaplan–Meier, log-rank test, and Cox PH regression
│   ├── visualization.py           # Plotly interactive charting library
│   ├── interpretation.py          # Clinical findings and interpretation engine
│   ├── report_generator.py        # ReportLab PDF report generation & CSV exports
│   ├── reproducibility.py         # Provenance, environment, and parameter tracking
│   └── ui_theme.py                # CSS design system, dark mode overrides, HTML components
├── tests/
│   ├── test_data_loader.py
│   ├── test_preprocessing.py
│   ├── test_hypothesis_testing.py
│   ├── test_survival_analysis.py
│   └── test_report_generator.py
├── reports/                       # Generated PDF and CSV outputs
└── docs/
    ├── methodology.md             # In-depth statistical methodology
    ├── data_dictionary.md         # Schema and clinical column dictionary
    └── limitations.md             # Methodological limitations and assumptions
```

---

## Quick Start

### 1. Prerequisites
Ensure you have **Python 3.10+** (Python 3.12 recommended) installed on your system.

### 2. Setup Virtual Environment
```bash
# Clone or navigate into the repository
cd ds-project

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch Application
```bash
streamlit run app.py
```
Open your browser and navigate to **`http://localhost:8501`**.

---

## Application Modules & Workflow

```
                                ┌───────────────────────────┐
                                │         Home Page         │
                                │  Overview & Metric Strip  │
                                └─────────────┬─────────────┘
                                              │
               ┌──────────────────────────────┼──────────────────────────────┐
               │                              │                              │
               ▼                              ▼                              ▼
 ┌───────────────────────────┐  ┌───────────────────────────┐  ┌───────────────────────────┐
 │     Patient Analytics     │  │            EDA            │  │    Hypothesis Testing     │
 │  Filters, KPIs & Outcome  │  │  6 Analytical Tabs, Heat- │  │  Parametric, Non-param.,  │
 │  Distributions by Stage   │  │  maps, & Outlier Analyses │  │  Effect Sizes & CIs       │
 └───────────────────────────┘  └───────────────────────────┘  └─────────────┬─────────────┘
                                                                             │
                                              ┌──────────────────────────────┘
                                              │
                                              ▼
                                ┌───────────────────────────┐
                                │     Survival Analysis     │
                                │  Kaplan-Meier, Log-Rank,  │
                                │  & Cox PH Forest Plots    │
                                └─────────────┬─────────────┘
                                              │
                                              ▼
                                ┌───────────────────────────┐
                                │          Reports          │
                                │  Clinical Synthesis, CSV  │
                                │  Exports & PDF Generator  │
                                └───────────────────────────┘
```

### 🏠 1. Home
- Executive summary of the patient survival research platform.
- Live cohort metric cards computing Total Patients, Observed Event Rate, Median Age, and Median Follow-up from active data.
- Quick-launch navigation cards directly linking to each analytical module.

### 📊 2. Patient Analytics
- **Cohort Filters**: Interactive filtering by age slider and categorical attributes (biological sex, disease stage, subtype, treatment arm, region).
- **KPI Summary Strip**: Real-time record counts, observed events, censored counts, event rate percentage, and median follow-up.
- **Visual Analytics**: Interactive Plotly charts for outcome distribution (pie chart), age distribution (histogram), patient distributions by sex and stage (bar charts), and event rates broken down by stage and treatment.
- **Dataset Replacement**: Optional upload drawer to replace the active dataset with a custom CSV or Excel file and remap analytical columns.

### 🔍 3. Exploratory Data Analysis (EDA)
Organized into 6 comprehensive analytical tabs:
1. **Descriptive Stats**: Full table of numeric variable statistics and expandable raw data preview.
2. **Numeric Distributions**: Interactive variable selector with histogram and box plot (with optional categorical grouping).
3. **Categorical**: Frequency bar charts and tabular counts for categorical clinical features.
4. **Missing Values**: Missingness heatmap and per-variable missing percentages with diagnostic notes.
5. **Correlation**: Heatmap matrix showing Pearson correlation across all numerical variables.
6. **Group Comparisons**: Proportion charts and breakdown tables comparing binary outcomes across selected cohorts.

### 🔬 4. Hypothesis Testing
- **Test Configuration**: Select between Two-Proportion Z-Test, Chi-Square Test, Welch's t-Test, and Kruskal–Wallis Test.
- **Significance Level & Corrections**: Adjust significance level ($\alpha \in [0.01, 0.10]$) and choose multiple-testing corrections (Holm step-down, Benjamini–Hochberg FDR, or unadjusted).
- **Execution**: Dynamic parameter inputs tailored to the selected test (outcome variable, reference group, comparison group, event definition).
- **Results Card**: Formatted display of sample size ($n$), test statistic, p-value, effect size (Risk Difference, Odds Ratio, Cohen's d, Cramér's V, or $\eta^2$), confidence intervals, expandable statistical hypotheses/assumptions, and automated plain-English interpretations.

### 📈 5. Survival Analysis
- **Follow-up Distribution**: Histogram of follow-up times stratified by event vs. censored status.
- **Overall Kaplan–Meier Curve**: Survival curve with confidence intervals and median survival benchmark.
- **Group Stratification & Log-Rank**: Stratified survival curves across clinical categories (e.g., stage, treatment arm, age groups) with numbers-at-risk table and log-rank test statistic ($\chi^2$, df, p-value).
- **Cox Proportional Hazards Regression**: Multivariable regression model computing hazard ratios (HR), 95% confidence intervals, p-values, concordance index (C-index), forest plots, and assumption checks.

### 📄 6. Reports & Reproducibility
- **Synthesized Clinical Findings**: Auto-generated text synthesizing results across all completed hypothesis tests, survival curves, and multivariable models.
- **Methodological Limitations**: Explicit documentation of observational constraints, non-causal inference, and proportional hazards assumptions.
- **Reproducibility Record**: Complete environment and run configuration (random seed, alpha, column mappings, package versions).
- **Data & Results Export**: Download analytical clean CSV, hypothesis test results CSV, and Cox regression tables.
- **PDF Report Generation**: Compiles an official, publication-ready PDF report using ReportLab containing clinical findings, tables, limitations, and provenance metadata.

---

## Statistical Methodology Reference

| Method | Primary Clinical Question | Assumptions & Notes |
|---|---|---|
| **Two-Proportion Z-Test** | Does 5-year survival rate differ between two treatment arms? | Independent samples; expected cell counts $\ge 5$; Wilson score CI. |
| **Fisher's Exact Test** | Does survival rate differ between rare subgroup cohorts? | Exact hypergeometric distribution used when cell counts are sparse ($<5$). |
| **Chi-Square Test** | Is disease stage associated with 5-year survival status? | Independent observations; minimum expected cell frequency $\ge 5$. |
| **Welch's t-Test** | Does mean patient age differ between event and censored groups? | Continuous numeric data; does not assume equal variances between groups. |
| **Kruskal–Wallis Test** | Does follow-up time distribution differ across multiple stages? | Non-parametric test based on ranked data; handles non-normal distributions. |
| **Holm Adjustment** | How do we control family-wise error rate across multiple tests? | Sequentially rejective procedure; less conservative than standard Bonferroni. |
| **Benjamini–Hochberg** | How do we control False Discovery Rate across multiple comparisons? | Ranks p-values to control expected proportion of false positive findings. |
| **Kaplan–Meier Estimator** | What is the cumulative probability of surviving past $t$ months? | Non-informative right censoring; handles censored observations appropriately. |
| **Log-Rank Test** | Are survival curves statistically significantly different across cohorts? | Compares observed vs. expected events across all discrete event time points. |
| **Cox Proportional Hazards** | What is the hazard ratio of Stage IV vs. Stage I adjusting for age and sex? | Semi-parametric model; assumes hazard ratios remain constant over time. |

---

## Input Data Schema

The platform accepts CSV and Excel files. When uploading your own dataset, the minimum required columns are:

| Column Role | Expected Data Type | Description | Example Values |
|---|---|---|---|
| **Patient ID** | String / Integer | Unique patient identifier | `P00001`, `10492` |
| **Age** | Numeric | Patient age at diagnosis | `45`, `62.5` |
| **Sex** | Categorical | Biological sex | `Male`, `Female` |
| **Disease Stage** | Categorical | Clinical staging | `Stage I`, `Stage II`, `Stage III`, `Stage IV` |
| **Follow-up Time** | Numeric (Positive) | Observation duration from diagnosis | `12.4`, `36.0`, `65.2` |
| **Event Indicator** | Binary (0 / 1) | Event of interest occurred (1 = event, 0 = censored) | `1`, `0` |
| **Binary Outcome** | Binary (0 / 1) | Fixed-time clinical endpoint (e.g., 5-year survival) | `1`, `0` |

---

## Automated Testing & Quality Assurance

The codebase includes an automated test suite verifying data loaders, schema validation, preprocessing pipelines, statistical calculations, survival models, and report generators.

To run tests:
```bash
pytest tests/ -v
```

To run tests with code coverage analysis:
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Methodological Limitations

- **Observational Nature**: This application analyzes observational clinical cohorts. Statistical associations do not imply causation.
- **Default Synthetic Data**: The pre-loaded dataset is synthetically generated with NumPy random seed 42 for testing and demonstration purposes. It does not represent real patient health records.
- **Missing Data Handling**: The current pipeline handles missing critical data via complete-case analysis. Missing covariates are reported in the data audit log.
- **Proportional Hazards Assumption**: The Cox proportional hazards model assumes constant hazard ratios over follow-up duration. If time-varying effects exist, hazard ratios represent an average effect over time.
- **Competing Risks**: Competing mortality risks (e.g., non-disease-related mortality) are treated as right-censoring.

---

## License & Attribution

This project is open-source under the MIT License. Developed for clinical biostatistics education, epidemiological exploration, and survival analysis prototyping.
