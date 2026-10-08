import json


def load_qc_findings(findings_file):
    """Load QC findings for agent input."""

    with open(findings_file) as f:
        return json.load(f)

def build_agent_input(findings):
    """Build structured input for the future AI agent."""

    samples = {}

    for finding in findings:
        sample = finding["Sample"]

        if sample not in samples:
            samples[sample] = {
                "sample": sample,
                "qc_status": finding["status"],
                "findings": []
            }

        samples[sample]["findings"].append({
            "finding": finding["finding"],
            "read": finding["read"],
            "observed": finding["observed"],
            "threshold": finding["threshold"],
            "severity": finding["severity"]
        })

    return {
        "samples": list(samples.values())
    }
