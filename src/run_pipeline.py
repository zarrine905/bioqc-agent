import sys
from pathlib import Path

from src.qc_engine import main as run_qc


def main():
    """Run the BioQC deterministic QC pipeline."""

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

    run_qc()

    findings_file = Path("results/qc_findings.json")

    if findings_file.exists():
        print(f"\nQC findings available at: {findings_file}")
    else:
        print("\nWarning: QC findings file was not generated.")

    print("\nPipeline completed.")


if __name__ == "__main__":
    main()
