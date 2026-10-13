from pathlib import Path
import argparse
import gzip
import yaml
import csv
import json
import subprocess

from src.fastqc_parser import parse_fastqc

def load_qc_thresholds(config_file):
    """Load QC thresholds from YAML configuration."""

    config_file = Path(config_file)

    with open(config_file) as f:
        config = yaml.safe_load(f)

    return config["qc_thresholds"]

def run_fastqc(data_dir, fastqc_dir):
    """Run FastQC on unique FASTQ files."""

    data_dir = Path(data_dir)
    fastqc_dir = Path(fastqc_dir)

    fastqc_dir.mkdir(parents=True, exist_ok=True)

    fastq_files = {}

    for fastq in data_dir.glob("*.fastq"):
        fastq_files[fastq.name] = fastq

    for fastq in data_dir.glob("*.fastq.gz"):
        uncompressed_name = fastq.name.replace(".gz", "")

        # Prefer compressed FASTQ if both exist
        fastq_files[uncompressed_name] = fastq

    fastq_files = list(fastq_files.values())

    if not fastq_files:
        raise FileNotFoundError(
            f"No FASTQ files found in {data_dir}"
        )

    command = [
        "fastqc",
        *[str(f) for f in fastq_files],
        "--outdir",
        str(fastqc_dir),
    ]

    print("\nRunning FastQC...")

    subprocess.run(command, check=True)

    print("FastQC completed.")



def count_fastq_reads(fastq_file):
    """Count reads in a FASTQ or FASTQ.GZ file."""

    fastq_file = Path(fastq_file)

    if fastq_file.name.endswith(".gz"):
        opener = gzip.open
    else:
        opener = open

    with opener(fastq_file, "rt") as f:
        line_count = sum(1 for _ in f)

    if line_count % 4 != 0:
        raise ValueError(
            f"Invalid FASTQ format: {fastq_file} "
            f"contains {line_count} lines, not divisible by 4."
        )

    return line_count // 4



def get_sample_name(filename):
    """Extract sample name from supported R1 FASTQ filename formats."""
    filename = Path(filename).name

    suffixes = (
        "_R1_001.fastq.gz",
        "_R1_001.fastq",
        "_R1.fastq.gz",
        "_R1.fastq",
    )

    for suffix in suffixes:
        if filename.endswith(suffix):
            return filename[:-len(suffix)]

    return None


def analyze_sample(r1_file, r2_file):
    """Calculate basic paired-end sequencing statistics."""

    r1_reads = count_fastq_reads(r1_file)
    r2_reads = count_fastq_reads(r2_file)

    if r1_reads != r2_reads:
        raise ValueError(
            f"R1/R2 read count mismatch for {r1_file} and {r2_file}: "
            f"R1={r1_reads}, R2={r2_reads}"
        )

    read_pairs = r1_reads
    total_reads = r1_reads + r2_reads

    return {
        "Sample": get_sample_name(r1_file),
        "R1_reads": r1_reads,
        "R2_reads": r2_reads,
        "Read_pairs": read_pairs,
        "Total_individual_reads": total_reads,
        "Total_M_reads": total_reads / 1_000_000,
    }




def apply_qc_rules(result, thresholds):
    """Apply deterministic QC rules using configured thresholds."""

    adapter_threshold = thresholds["adapter_percent"]
    n_threshold = thresholds["n_percent"]

    flags = []

    if result["R1_N_%"] > n_threshold:
        flags.append("R1_HIGH_N")

    if result["R2_N_%"] > n_threshold:
        flags.append("R2_HIGH_N")

    if result["R1_Adapter_%"] > adapter_threshold:
        flags.append("R1_HIGH_ADAPTER")

    if result["R2_Adapter_%"] > adapter_threshold:
        flags.append("R2_HIGH_ADAPTER")

    if flags:
        result["QC_status"] = "FAIL"
        result["QC_flags"] = ";".join(flags)
    else:
        result["QC_status"] = "PASS"
        result["QC_flags"] = ""

    return result

def build_qc_findings(result, thresholds):
    """Build structured QC findings for downstream interpretation."""

    findings = []

    n_threshold = thresholds["n_percent"]
    adapter_threshold = thresholds["adapter_percent"]

    if result["R1_N_%"] > n_threshold:
        findings.append({
            "Sample": result["Sample"],
            "status": "FAIL",
            "finding": "HIGH_N_CONTENT",
            "read": "R1",
            "observed": result["R1_N_%"],
            "threshold": n_threshold,
            "severity": "HIGH"
        })

    if result["R2_N_%"] > n_threshold:
        findings.append({
            "Sample": result["Sample"],
            "status": "FAIL",
            "finding": "HIGH_N_CONTENT",
            "read": "R2",
            "observed": result["R2_N_%"],
            "threshold": n_threshold,
            "severity": "HIGH"
        })

    if result["R1_Adapter_%"] > adapter_threshold:
        findings.append({
            "Sample": result["Sample"],
            "status": "FAIL",
            "finding": "HIGH_ADAPTER_CONTENT",
            "read": "R1",
            "observed": result["R1_Adapter_%"],
            "threshold": adapter_threshold,
            "severity": "HIGH"
        })

    if result["R2_Adapter_%"] > adapter_threshold:
        findings.append({
            "Sample": result["Sample"],
            "status": "FAIL",
            "finding": "HIGH_ADAPTER_CONTENT",
            "read": "R2",
            "observed": result["R2_Adapter_%"],
            "threshold": adapter_threshold,
            "severity": "HIGH"
        })

    return findings



def discover_samples(data_dir):
    """Find paired-end FASTQ files across supported naming conventions."""
    data_dir = Path(data_dir)

    patterns = (
        "*_R1.fastq",
        "*_R1.fastq.gz",
        "*_R1_001.fastq",
        "*_R1_001.fastq.gz",
    )

    r1_files = []
    for pattern in patterns:
        r1_files.extend(data_dir.glob(pattern))

    sample_r1 = {}
    for r1 in r1_files:
        sample = get_sample_name(r1.name)
        if sample is not None:
            sample_r1.setdefault(sample, []).append(r1)

    samples = []

    for sample in sorted(sample_r1):
        # Prefer compressed files when their matching R2 exists.
        candidates = sorted(
            sample_r1[sample],
            key=lambda p: (not p.name.endswith(".gz"), p.name),
        )

        for r1 in candidates:
            if r1.name.endswith("_R1_001.fastq.gz"):
                r2_name = r1.name.replace(
                    "_R1_001.fastq.gz", "_R2_001.fastq.gz"
                )
            elif r1.name.endswith("_R1_001.fastq"):
                r2_name = r1.name.replace(
                    "_R1_001.fastq", "_R2_001.fastq"
                )
            elif r1.name.endswith("_R1.fastq.gz"):
                r2_name = r1.name.replace(
                    "_R1.fastq.gz", "_R2.fastq.gz"
                )
            else:
                r2_name = r1.name.replace(
                    "_R1.fastq", "_R2.fastq"
                )

            r2 = data_dir / r2_name

            if r2.exists():
                samples.append((r1, r2))
                break
        else:
            print(f"WARNING: No matching R2 file found for {sample}")

    print(f"Discovered {len(samples)} paired samples in {data_dir}")
    return samples


def write_tsv(results, output_file):
    """Write sample QC results to a TSV file."""

    output_file = Path(output_file)

    fieldnames = [
        "Sample",
        "R1_reads",
        "R2_reads",
        "Read_pairs",
        "Total_individual_reads",
        "Total_M_reads",
        "R1_N_%",
        "R2_N_%",
        "R1_Adapter_%",
        "R2_Adapter_%",
        "QC_status",
        "QC_flags",
    ]

    with open(output_file, "w", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter="\t"
        )

        writer.writeheader()
        writer.writerows(results)


def main():

    parser = argparse.ArgumentParser(
        description="Sample-wise paired-end FASTQ QC engine"
    )

    parser.add_argument(
        "--data-dir",
        default="data/raw",
        help="Directory containing FASTQ files"
    )

    parser.add_argument(
        "--output",
        default="results/sample_qc.tsv",
        help="Output TSV file"
    )

    parser.add_argument(
        "--fastqc-dir",
        default="results/fastqc",
        help="Directory containing FastQC ZIP files"
    )

    parser.add_argument(
    "--config",
    default="config/qc_thresholds.yaml",
    help="QC threshold configuration YAML file"
    )

    args = parser.parse_args()
    thresholds = load_qc_thresholds(args.config)

    samples = discover_samples(args.data_dir)
    run_fastqc(args.data_dir, args.fastqc_dir)

    if not samples:
        print("No FASTQ sample pairs found.")
        return

    results = []
    findings = []

    for r1, r2 in samples:

        result = analyze_sample(r1, r2)

        sample = result["Sample"]

        # Expected FastQC files for paired-end sample

        # Find FastQC reports for both supported naming conventions.
        fastqc_dir = Path(args.fastqc_dir)

        r1_candidates = [
            fastqc_dir / f"{sample}_R1_fastqc.zip",
            fastqc_dir / f"{sample}_R1_001_fastqc.zip",
        ]
        r2_candidates = [
            fastqc_dir / f"{sample}_R2_fastqc.zip",
            fastqc_dir / f"{sample}_R2_001_fastqc.zip",
        ]

        r1_fastqc = next(
            (p for p in r1_candidates if p.exists()), None
        )
        r2_fastqc = next(
            (p for p in r2_candidates if p.exists()), None
        )

        if r1_fastqc is not None and r2_fastqc is not None:
            r1_metrics = parse_fastqc(r1_fastqc)
            r2_metrics = parse_fastqc(r2_fastqc)

            result["R1_N_%"] = r1_metrics["N_percent"]
            result["R2_N_%"] = r2_metrics["N_percent"]
            result["R1_Adapter_%"] = r1_metrics["Adapter_percent"]
            result["R2_Adapter_%"] = r2_metrics["Adapter_percent"]
        else:
            print(f"WARNING: FastQC results missing for {sample}")
            print(f"  R1 report: {r1_fastqc}")
            print(f"  R2 report: {r2_fastqc}")

            result["R1_N_%"] = None
            result["R2_N_%"] = None
            result["R1_Adapter_%"] = None
            result["R2_Adapter_%"] = None

        result = apply_qc_rules(result, thresholds)
        findings.extend(build_qc_findings(result, thresholds))
        results.append(result)

        # Terminal summary
        print(f"\nSample: {result['Sample']}")
        print(f"R1 reads: {result['R1_reads']}")
        print(f"R2 reads: {result['R2_reads']}")
        print(f"Read pairs: {result['Read_pairs']}")

        print(
            f"Total individual reads: "
            f"{result['Total_individual_reads']}"
        )

        print(
            f"Total million reads: "
            f"{result['Total_M_reads']:.6f}"
        )

        print(
            f"R1 N %: "
            f"{result['R1_N_%']}"
        )

        print(
            f"R2 N %: "
            f"{result['R2_N_%']}"
        )

        print(
            f"R1 Adapter %: "
            f"{result['R1_Adapter_%']}"
        )

        print(
            f"R2 Adapter %: "
            f"{result['R2_Adapter_%']}"
        )

    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    write_tsv(results, output_file)
    findings_file = output_file.parent / "qc_findings.json"

    with open(findings_file, "w") as f:
        json.dump(findings, f, indent=2)

    print(f"QC findings written to: {findings_file}")

    print(
        f"\nQC table written to: {args.output}"
    )


if __name__ == "__main__":
    main()
