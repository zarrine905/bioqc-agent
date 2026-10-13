
import json
from pathlib import Path

import pandas as pd


def load_qc_findings(findings_file):
    """Load deterministic QC findings."""
    with open(findings_file, encoding="utf-8") as f:
        return json.load(f)


def load_ml_findings(anomaly_file):
    """Load optional ML anomaly results, indexed by sample."""
    anomaly_file = Path(anomaly_file)

    if not anomaly_file.exists():
        return {}

    df = pd.read_csv(anomaly_file, sep="\t")

    required = {
        "Sample",
        "ML_anomaly_score",
        "ML_anomaly",
        "ML_assessment",
        "ML_explanation",
    }
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Anomaly file is missing columns: {sorted(missing)}"
        )

    def parse_bool(value):
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"true", "1", "yes"}

    ml_findings = {}

    for _, row in df.iterrows():
        sample = str(row["Sample"])
        ml_findings[sample] = {
            "ml_anomaly_score": float(row["ML_anomaly_score"]),
            "ml_anomaly": parse_bool(row["ML_anomaly"]),
            "ml_assessment": str(row["ML_assessment"]),
            "ml_explanation": str(row["ML_explanation"]),
        }

    return ml_findings


def build_agent_input(findings, ml_findings=None, qc_table=None):
    """Combine every QC sample with deterministic findings and optional ML results."""
    ml_findings = ml_findings or {}
    samples = {}

    # Start with the complete QC table so PASS samples are included.
    if qc_table is not None:
        qc_table = Path(qc_table)

        if qc_table.exists():
            df = pd.read_csv(qc_table, sep="\t")

            required = {"Sample", "QC_status"}
            missing = required - set(df.columns)

            if missing:
                raise ValueError(
                    f"QC table is missing columns: {sorted(missing)}"
                )

            for _, row in df.iterrows():
                sample = str(row["Sample"])
                samples[sample] = {
                    "sample": sample,
                    "qc_status": str(row["QC_status"]),
                    "findings": [],
                }

    # Add the detailed deterministic findings.
    for finding in findings:
        sample = str(finding["Sample"])

        if sample not in samples:
            samples[sample] = {
                "sample": sample,
                "qc_status": finding["status"],
                "findings": [],
            }

        samples[sample]["findings"].append({
            "finding": finding["finding"],
            "read": finding["read"],
            "observed": finding["observed"],
            "threshold": finding["threshold"],
            "severity": finding["severity"],
        })

    # Attach ML results separately; never change deterministic QC status.
    for sample, ml_result in ml_findings.items():
        if sample not in samples:
            samples[sample] = {
                "sample": sample,
                "qc_status": "NOT_PROVIDED",
                "findings": [],
            }

        samples[sample]["ml"] = ml_result

    # Make missing ML status explicit for every sample.
    for sample_data in samples.values():
        sample_data.setdefault("ml", None)

    return {"samples": list(samples.values())}
