"""Reproducibility: record analysis settings and environment for audit."""

from __future__ import annotations

import datetime
import importlib
import json
import platform
import sys
from typing import Any


TRACKED_PACKAGES = [
    "streamlit", "pandas", "numpy", "scipy", "statsmodels",
    "lifelines", "plotly", "sklearn", "reportlab",
]


def get_package_versions() -> dict[str, str]:
    versions = {"python": sys.version.split()[0]}
    for pkg in TRACKED_PACKAGES:
        try:
            mod = importlib.import_module(pkg)
            versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            versions[pkg] = "not installed"
    return versions


def build_reproducibility_record(
    dataset_name: str,
    dataset_source: str,
    column_mapping: dict[str, str],
    preprocessing_settings: dict[str, Any],
    analysis_settings: dict[str, Any],
    random_seed: int,
) -> dict:
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "platform": platform.platform(),
        "dataset_name": dataset_name,
        "dataset_source": dataset_source,
        "column_mapping": column_mapping,
        "preprocessing_settings": preprocessing_settings,
        "analysis_settings": analysis_settings,
        "random_seed": random_seed,
        "package_versions": get_package_versions(),
    }


def reproducibility_to_text(record: dict) -> str:
    lines = [
        "=== REPRODUCIBILITY RECORD ===",
        f"Timestamp       : {record.get('timestamp', 'N/A')}",
        f"Platform        : {record.get('platform', 'N/A')}",
        f"Dataset         : {record.get('dataset_name', 'N/A')}",
        f"Source          : {record.get('dataset_source', 'N/A')}",
        f"Random Seed     : {record.get('random_seed', 'N/A')}",
        "",
        "Column Mapping:",
    ]
    for k, v in record.get("column_mapping", {}).items():
        lines.append(f"  {k}: {v}")
    lines += ["", "Package Versions:"]
    for k, v in record.get("package_versions", {}).items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def reproducibility_to_json(record: dict) -> str:
    return json.dumps(record, indent=2, default=str)
