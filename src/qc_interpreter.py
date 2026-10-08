import json


def load_findings(findings_file):
    """Load structured QC findings from JSON."""

    with open(findings_file) as f:
        return json.load(f)

def explain_finding(finding):
    """Convert a structured QC finding into a human-readable explanation."""

    if finding["finding"] == "HIGH_N_CONTENT":
        return (
            f"{finding['Sample']} failed QC because {finding['read']} has "
            f"{finding['observed']}% N content, exceeding the configured "
            f"threshold of {finding['threshold']}%."
        )

    if finding["finding"] == "HIGH_ADAPTER_CONTENT":
        return (
            f"{finding['Sample']} failed QC because {finding['read']} has "
            f"{finding['observed']}% adapter content, exceeding the configured "
            f"threshold of {finding['threshold']}%."
        )

    return (
        f"{finding['Sample']} has a QC finding: "
        f"{finding['finding']}."
    )

def recommend_action(finding):
    """Recommend a next check based on the QC finding."""

    if finding["finding"] == "HIGH_N_CONTENT":
        return (
            f"Check {finding['read']} sequencing/base-calling quality "
            f"and review the FastQC report before downstream analysis."
        )

    if finding["finding"] == "HIGH_ADAPTER_CONTENT":
        return (
            f"Review adapter contamination in {finding['read']} "
            f"and consider adapter trimming before downstream analysis."
        )

    return "Review the FastQC report for additional QC information."

def interpret_finding(finding):
    """Create a complete interpretation of a QC finding."""

    return {
        "Sample": finding["Sample"],
        "status": finding["status"],
        "severity": finding["severity"],
        "finding": finding["finding"],
        "explanation": explain_finding(finding),
        "recommended_action": recommend_action(finding),
    }

def interpret_all_findings(findings):
    """Interpret all QC findings."""

    interpretations = []

    for finding in findings:
        interpretations.append(interpret_finding(finding))

    return interpretations


def explain_all_findings(findings):
    """Generate explanations for all QC findings."""

    explanations = []

    for finding in findings:
        explanations.append(explain_finding(finding))

    return explanations

if __name__ == "__main__":
    findings = load_findings("results/qc_findings.json")

    interpretations = interpret_all_findings(findings)

    print("=" * 40)
    print("QC INTERPRETATION")
    print("=" * 40)

    for interpretation in interpretations:
        print()
        print(f"Sample: {interpretation['Sample']}")
        print(f"Status: {interpretation['status']}")
        print(f"Severity: {interpretation['severity']}")
        print(f"Finding: {interpretation['finding']}")

        print("\nExplanation:")
        print(interpretation["explanation"])

        print("\nRecommended action:")
        print(interpretation["recommended_action"])
