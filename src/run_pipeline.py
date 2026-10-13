import re
import sys
from pathlib import Path

from src.qc_engine import main as run_qc
from src.agent_input import (
    load_qc_findings,
    load_ml_findings,
    build_agent_input,
)
from src.agent_prompt import build_agent_prompt
from src.llm_client import ask_llm
from src.qc_anomaly_detector import detect_anomalies


def validate_interpretation(interpretation, agent_input):
    """Check sample coverage and authoritative QC statuses."""
    errors = []
    sample_data = agent_input.get("samples", [])

    # Locate sample sections in the LLM response.
    headings = list(re.finditer(
        r"^Sample:\s*(.+?)\s*$",
        interpretation,
        flags=re.MULTILINE,
    ))

    sections = {}

    for i, match in enumerate(headings):
        sample_name = match.group(1).strip()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(interpretation)
        sections.setdefault(sample_name, []).append(
            interpretation[match.start():end]
        )

    for sample in sample_data:
        name = str(sample["sample"])
        expected_status = str(sample["qc_status"])

        if name not in sections:
            errors.append(f"Missing sample: {name}")
            continue

        if len(sections[name]) != 1:
            errors.append(f"Sample appears more than once: {name}")
            continue

        status_match = re.search(
            r"^Deterministic QC status:\s*(PASS|FAIL|NOT_PROVIDED)\s*$",
            sections[name][0],
            flags=re.MULTILINE | re.IGNORECASE,
        )

        if not status_match:
            errors.append(f"Missing or invalid QC status for {name}")
        elif status_match.group(1).upper() != expected_status.upper():
            errors.append(
                f"Status mismatch for {name}: expected {expected_status}, "
                f"received {status_match.group(1).upper()}"
            )

    return errors



def build_safe_report(agent_input):
    """Build a report from structured QC and ML data without LLM guesses."""
    report = []

    for sample in agent_input.get("samples", []):
        name = sample["sample"]
        status = sample["qc_status"]
        findings = sample.get("findings", [])
        ml = sample.get("ml")

        report.extend([
            f"Sample: {name}",
            f"Deterministic QC status: {status}",
            "QC findings:",
        ])

        if findings:
            for finding in findings:
                label = finding["finding"]
                read = finding["read"]
                observed = finding["observed"]
                threshold = finding["threshold"]
                severity = finding["severity"]

                unit = "%" if label in {
                    "HIGH_N_CONTENT",
                    "HIGH_ADAPTER_CONTENT",
                } else ""

                report.append(
                    f"- {label}, {read}, observed {observed}{unit}, "
                    f"threshold {threshold}{unit}, severity {severity}"
                )
        else:
            report.append("- No deterministic QC findings were provided.")

        if ml:
            assessment = ml.get("ml_assessment", "Not available")
            score = ml.get("ml_anomaly_score", "Not available")
            explanation = ml.get("ml_explanation", "Not available")
        else:
            assessment = "Not available"
            score = "Not available"
            explanation = "Not available"

        report.extend([
            f"ML assessment: {assessment}",
            f"ML anomaly score: {score}",
            f"ML explanation: {explanation}",
        ])

        # Interpretation follows deterministic QC and ML evidence separately.
        if status == "FAIL":
            interpretation = (
                "The sample failed the implemented deterministic QC checks."
            )
        elif status == "PASS":
            interpretation = (
                "The sample passed the implemented deterministic QC checks; "
                "this does not establish suitability for every downstream use."
            )
        else:
            interpretation = (
                "A deterministic QC status was not provided."
            )

        report.append(f"Interpretation: {interpretation}")
        report.append("Recommended checks:")

        recommendations = []

        # Recommendations for deterministic QC findings.
        for finding in findings:
            if finding["finding"] == "HIGH_N_CONTENT":
                recommendations.append(
                    f"Review the FastQC N-content plot for {finding['read']} "
                    "and investigate sequencing/base-calling quality."
                )
            elif finding["finding"] == "HIGH_ADAPTER_CONTENT":
                recommendations.append(
                    f"Review adapter content for {finding['read']} and assess "
                    "whether adapter trimming is appropriate."
                )

        # Recommendations for ML review signals.
        if ml and assessment == "REVIEW":
            explanation_lower = str(explanation).lower()

            if "low read count" in explanation_lower:
                recommendations.append(
                    "Inspect the reported read count and compare it with "
                    "the expected sequencing depth for the assay."
                )

            if (
                not recommendations
                and "high r1 n-content" not in explanation_lower
                and "high r2 n-content" not in explanation_lower
                and "high r1 adapter content" not in explanation_lower
                and "high r2 adapter content" not in explanation_lower
            ):
                recommendations.append(
                    "Review the supplied QC metrics and compare the sample "
                    "with appropriate peer samples."
                )

        if recommendations:
            # Remove duplicates while preserving order.
            recommendations = list(dict.fromkeys(recommendations))
            report.extend(f"- {item}" for item in recommendations)
        else:
            report.append(
                "- No additional checks indicated by the supplied findings."
            )

        report.append("")

    return "\n".join(report).strip()



def interpret_in_batches(agent_input, batch_size=5):
    """Run the LLM for draft interpretations, but build the final
    report from structured QC and ML data for consistent output.
    """
    samples = agent_input.get("samples", [])
    llm_drafts = []

    for start in range(0, len(samples), batch_size):
        batch_samples = samples[start:start + batch_size]
        batch_input = {
            **agent_input,
            "samples": batch_samples,
        }

        prompt = build_agent_prompt(batch_input)

        try:
            draft = ask_llm(prompt)
            llm_drafts.append(
                f"LLM draft for samples {start + 1}-"
                f"{start + len(batch_samples)}\n"
                f"{draft}\n"
            )
        except Exception as exc:
            llm_drafts.append(
                f"LLM draft for samples {start + 1}-"
                f"{start + len(batch_samples)}\n"
                f"LLM error: {exc}\n"
            )

    # Preserve the model's output for debugging and comparison.
    with open(
        "results/ai_qc_llm_draft.txt", "w", encoding="utf-8"
    ) as handle:
        handle.write("\n".join(llm_drafts))

    # The final report uses the structured evidence, not free-form text.
    return build_safe_report(agent_input)


def main():
    """Run deterministic QC, optional ML screening, and LLM interpretation."""

    print("=" * 60)
    print("BioQC-Agent")
    print("Starting automated QC pipeline")
    print("=" * 60)

    sys.argv = [
        "run_pipeline",
        "--data-dir", "data/test",
        "--output", "results/sample_qc.tsv",
        "--fastqc-dir", "results/fastqc",
        "--config", "config/qc_thresholds.yaml",
    ]

    # Step 1: Deterministic QC remains authoritative.
    run_qc()

    findings_file = Path("results/qc_findings.json")
    qc_table = Path("results/sample_qc.tsv")
    anomaly_file = Path("results/qc_anomalies.tsv")

    if not findings_file.exists():
        print("\nError: QC findings file was not generated.")
        return

    if not qc_table.exists():
        print("\nError: Sample QC table was not generated.")
        return

    print(f"\nQC findings available at: {findings_file}")

    # Step 2: Run ML screening if enough usable samples exist.
    ml_findings = {}

    try:
        detect_anomalies(qc_table, anomaly_file)
        ml_findings = load_ml_findings(anomaly_file)
    except ValueError as exc:
        print(f"\nML screening unavailable: {exc}")
        print("Continuing with deterministic QC findings.")
    except Exception as exc:
        print(f"\nML screening error: {exc}")
        print("Continuing with deterministic QC findings.")

    # Step 3: Build combined structured input.
    findings = load_qc_findings(findings_file)
    agent_input = build_agent_input(
        findings,
        ml_findings,
        qc_table=qc_table,
    )

    # Step 4: Interpret samples in small batches.
    print("\nGenerating AI QC interpretation in batches...")

    interpretation = interpret_in_batches(
        agent_input,
        batch_size=5,
    )

    # Step 5: Display the final combined report.
    print("\n" + "=" * 60)
    print("AI QC INTERPRETATION")
    print("=" * 60)
    print(interpretation)

    # Step 6: Save interpretation.
    interpretation_file = Path("results/ai_qc_interpretation.txt")
    interpretation_file.parent.mkdir(parents=True, exist_ok=True)
    interpretation_file.write_text(interpretation, encoding="utf-8")

    print(f"\nAI interpretation written to: {interpretation_file}")
    print("\nPipeline completed.")


if __name__ == "__main__":
    main()
