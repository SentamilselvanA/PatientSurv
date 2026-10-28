"""Central configuration for the patient survival analysis application."""

RANDOM_SEED = 42
DEFAULT_ALPHA = 0.05
MAX_UPLOAD_MB = 50
APP_TITLE = "Comparative Statistical Analysis of Patient Survival Rates"
APP_VERSION = "1.0.0"

# Synthetic dataset generation
SYNTHETIC_N = 1000

# Survival analysis
DEFAULT_TIME_UNIT = "months"
KM_CONFIDENCE_TYPE = "log-log"

# Report
REPORT_DIR = "reports"
REPORT_AUTHOR = "Patient Survival Analysis Tool"

# Logging
LOG_LEVEL = "INFO"
