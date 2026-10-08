import sys
from pathlib import Path

from src.qc_engine import main as run_qc
from src.agent_input import load_qc_findings, build_agent_input
from src.agent_prompt import build_agent_prompt
from src.llm_client import ask_llm


def main():
    """Run the complete BioQC-Agent pipeline."""

    print("=" * 60)
    print("BioQC-Agent")
    print("Starting automated QC pipeline")
    print("=" * 60)

    sys.argv = [
        "run_pipeline",
        "--data-dir",
        "data/test",
        "--output",
        "results/sample_qc.tsv",
        "--fastqc-dir",
        "results/fastqc",
        "--config",
        "config/qc_thresholds.yaml",
    ]

    # Step 1: Deterministic QC
    run_qc()

    findings_file = Path("results/qc_findings.json")

    if not findings_file.exists():
        print("\nError: QC findings file was not generated.")
        return

    print(f"\nQC findings available at: {findings_file}")

    # Step 2: Build structured agent input
    findings = load_qc_findings(findings_file)
    agent_input = build_agent_input(findings)

    # Step 3: Build guarded LLM prompt
    prompt = build_agent_prompt(agent_input)

    # Step 4: Local Llama interpretation
    print("\nGenerating AI QC interpretation...")

    interpretation = ask_llm(prompt)

    print("\n" + "=" * 60)
    print("AI QC INTERPRETATION")
    print("=" * 60)
    print(interpretation)

    # Step 5: Save interpretation
    interpretation_file = Path("results/ai_qc_interpretation.txt")

    with open(interpretation_file, "w") as f:
        f.write(interpretation)

    print(f"\nAI interpretation written to: {interpretation_file}")
    print("\nPipeline completed.")


if __name__ == "__main__":
    main()
