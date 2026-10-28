# Data Dictionary

## Synthetic Dataset Variables

| Variable | Meaning | Type | Unit | Valid Values | Analytical Role |
|---|---|---|---|---|---|
| patient_id | Unique patient identifier | string | — | P00001–P01000 | Identifier |
| age | Age at diagnosis | numeric | years | 18–85 | Demographic |
| sex | Biological sex | categorical | — | Male, Female | Demographic |
| stage | Disease stage at diagnosis | categorical | — | I, II, III, IV | Clinical |
| subtype | Disease subtype | categorical | — | A, B, C | Clinical |
| treatment | Primary treatment received | categorical | — | Surgery, Chemo, Radiation, Combined | Clinical |
| follow_up_months | Duration from diagnosis to event or last contact | numeric | months | ≥ 0 | Time (survival) |
| event | Event indicator | binary | — | 0 = censored, 1 = event occurred | Outcome (survival) |
| survival_5yr | Five-year survival status | binary | — | 0 = no, 1 = yes | Outcome (binary) |
| comorbidity_score | Comorbidity burden index | numeric | — | 0–4 | Clinical |
| region | Geographic region of treatment | categorical | — | North, South, East, West | Demographic |

## Notes

- `follow_up_months` and `event` are the primary variables for time-to-event (Kaplan–Meier, Cox) analysis.
- `survival_5yr` is the primary variable for binary outcome analysis.
- `age_group` is a derived variable added during preprocessing.
- Missing values in `age` (~3%) and `follow_up_months` (~2%) are introduced to simulate real-world data quality.
- All values are synthetic and do not represent any real patient population.
