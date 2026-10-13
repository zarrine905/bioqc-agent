# BioQC-Agent: AI-Assisted NGS Quality Control

**Deterministic QC first. Machine learning second. AI-assisted interpretation third.**

BioQC-Agent is a Python-based bioinformatics project that combines FastQC, rule-based quality control, unsupervised machine learning, and a locally running large language model (LLM) to help researchers interpret next-generation sequencing (NGS) quality-control findings.

The project explores how AI can make sequencing QC easier to understand without replacing scientific rules or human review.

> **The rules decide. The ML model flags unusual patterns. The AI explains. The scientist decides.**

## 1. Project Overview

BioQC-Agent separates quality-control decisions from anomaly detection and AI-assisted interpretation.

### Workflow

```text
Synthetic or User FASTQ Files
            |
            v
          FastQC
            |
            v
     Python QC Engine
            |
            v
  Deterministic QC Findings
         PASS / FAIL
            |
            +-------------------+
            |                   |
            v                   v
   Structured Findings    QC Metrics for ML
                                |
                                v
                        Isolation Forest
                                |
                                v
                       Anomaly Assessment
            |                   |
            +---------+---------+
                      |
                      v
              AI Interpretation
                      |
                      v
                Ollama / LLM
                      |
                      v
             QC Summary and Report
                      |
                      v
                 Human Review
```

The deterministic QC engine remains the source of truth for rule-based PASS/FAIL decisions. Machine learning provides a separate anomaly assessment, while the LLM helps explain the available evidence.

## 2. Key Features

- Automated discovery of paired-end FASTQ files.
- FastQC-based sequencing quality assessment.
- Python-based deterministic QC rules.
- Configurable QC thresholds using YAML.
- Structured QC findings in JSON format.
- Sample-level QC summaries in TSV format.
- Isolation Forest-based anomaly detection.
- ML anomaly scores, flags, and review assessments.
- Local AI-assisted interpretation using Ollama and Llama 3.2 3B.
- Separation of deterministic QC status from ML anomaly flags.
- Synthetic FASTQ data, including an intentionally degraded sample for testing.
- Prompt constraints designed to reduce unsupported AI claims.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Pipeline orchestration and QC logic |
| FastQC | Sequencing quality assessment |
| PyYAML | QC configuration |
| pandas | QC tables and data processing |
| scikit-learn | Isolation Forest anomaly detection |
| Ollama | Local LLM runtime |
| Llama 3.2 3B | AI-assisted QC interpretation |
| JSON / TSV | Structured findings and reports |
| Git / GitHub | Version control and project hosting |

## 4. Synthetic Test Dataset

A small artificial paired-end FASTQ dataset is included in:

`data/synthetic/`

The dataset contains ten samples: nine baseline synthetic samples and one intentionally degraded sample.

| Sample | Description |
|---|---|
| `SYNTH_001`–`SYNTH_009` | Artificial baseline samples |
| `BAD` | Intentionally degraded sample used to test high N-content detection |

Each sample contains R1 and R2 FASTQ files, with 50 read pairs and a read length of 100 bases.

The `BAD` sample is designed to test whether the QC engine detects excessive ambiguous bases:

- `BAD_R1.fastq.gz` contains 100% N bases in its read sequences.
- `BAD_R2.fastq.gz` is the paired R2 file.
- The configured N-content threshold is 1%.
- The expected deterministic result is `FAIL`, with the QC flag `R1_HIGH_N`.

The dataset also includes:

- `README.md` — synthetic dataset description and limitations.
- `MANIFEST.tsv` — sample identifiers, paired filenames, and data type.

These sequences are artificial and are not biologically representative. The dataset contains no real patient sequencing data and is intended for software testing, not clinical validation or benchmarking of real-world QC performance.

## 5. Installation

BioQC-Agent has been developed in a Linux environment.

### Step 1: Clone the repository

Using HTTPS:

```bash
git clone https://github.com/zarrine905/bioqc-agent.git
cd bioqc-agent
```

Alternatively, use SSH if your GitHub SSH authentication is configured:

```bash
git clone git@github.com:zarrine905/bioqc-agent.git
cd bioqc-agent
```

### Step 2: Check Python

```bash
python3 --version
```

Python 3 is required. Use a compatible Python version for the project's dependencies.

### Step 3: Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If your existing environment is already configured, you can activate it instead.

### Step 4: Install Python dependencies

```bash
python -m pip install pyyaml pandas scikit-learn
```

Install any additional dependencies required by the current source files. If the repository provides a dependency file, prefer installing from that file to reproduce the intended environment.

### Step 5: Install FastQC

On Ubuntu or Debian:

```bash
sudo apt update
sudo apt install fastqc
```

Verify the installation:

```bash
fastqc --version
```

### Step 6: Install Ollama

Follow the official installation instructions:

https://ollama.com/download

Check that Ollama is available:

```bash
ollama --version
```

### Step 7: Download the local model

BioQC-Agent is configured to use Llama 3.2 3B through Ollama.

```bash
ollama pull llama3.2:3b
ollama list
```

Confirm that `llama3.2:3b` appears in the model list.

The local model avoids the need for an OpenAI API key or paid hosted-LLM API credits. Local inference still requires suitable computing resources.

## 6. Run the Pipeline

Run commands from the repository root, `bioqc-agent/`.

### Step 1: View the available options

```bash
python -m src.run_pipeline --help
```

The pipeline accepts options including:

- `--data-dir` — directory containing input FASTQ files.
- `--output` — output **file path** for the sample QC table.
- `--fastqc-dir` — FastQC output directory.
- `--config` — QC configuration file.

Run `python -m src.run_pipeline --help` to confirm the exact options supported by your installed version.

### Step 2: Run on the included synthetic dataset

```bash
python -m src.run_pipeline \
  --data-dir data/synthetic/
```

To explicitly specify the QC output file:

```bash
python -m src.run_pipeline \
  --data-dir data/synthetic/ \
  --output results/synthetic/sample_qc.tsv
```

**Important:** `--output` is a file path, not a directory. Use `results/synthetic/sample_qc.tsv`, rather than `results/synthetic`.

Run the module from the repository root using `python -m src.run_pipeline`. Running `python src/run_pipeline.py` may cause import errors because the code imports modules through the `src` package.

### Step 3: Inspect the results

List the generated files:

```bash
find results/synthetic -maxdepth 3 -type f | sort
```

Inspect the sample QC table:

```bash
cat results/synthetic/sample_qc.tsv
```

Inspect the structured QC findings:

```bash
python -m json.tool results/synthetic/qc_findings.json
```

Inspect ML anomaly assessments:

```bash
cat results/synthetic/qc_anomalies.tsv
```

The exact output files depend on the current pipeline configuration. The files generated by your actual run are the authoritative record.

## 7. Understanding QC Results

BioQC-Agent separates three types of assessment.

### A. Deterministic QC

The Python QC engine applies configured rules to supported metrics.

The current implementation includes checks for:

- N-content.
- Adapter content.

Thresholds are stored in:

`config/qc_thresholds.yaml`

The current N-content threshold is 1%, and the adapter-content threshold is 5%.

The configuration also contains a Q30 threshold value, but Q30 evaluation is not currently implemented. A configuration value alone does not mean that a metric is being evaluated.

Thresholds are project settings, not universal scientific standards. Production use requires assay- and platform-appropriate validation.

### B. Machine Learning Anomaly Detection

The ML layer uses Isolation Forest to identify samples with unusual combinations of QC metrics.

The intended feature set includes:

- Total reads in millions.
- R1 N-content.
- R2 N-content.
- R1 adapter content.
- R2 adapter content.

The ML component can generate an anomaly score, an anomaly flag, and a review assessment.

An anomaly score is not a probability of sequencing failure. A sample may pass deterministic QC and still be flagged by ML, or fail a QC rule without being flagged by ML.

The model's results depend on the analysed sample set, feature preprocessing, and model settings. A small synthetic dataset is suitable for a functional demonstration, but not for validating real-world anomaly detection performance.

### C. AI-Assisted Interpretation

The local LLM receives structured QC evidence and generates explanations or suggested follow-up checks.

For example, a high N-content finding may prompt a reviewer to investigate read quality, base-calling performance, or relevant sequencing-run QC metrics.

These are possible investigation steps, not proof of the cause of a QC failure.

The AI layer is intended to explain the available evidence rather than independently determine whether a sample passes QC.

Prompt constraints can reduce unsupported claims, but they cannot guarantee that an LLM will always produce accurate output.

## 8. Demonstration: Detecting High N-Content

The synthetic `BAD` sample provides a reproducible test of the deterministic QC engine and ML screening layer.

The observed output includes:

| Metric | Observed result |
|---|---|
| Sample | `BAD` |
| R1 reads | 50 |
| R2 reads | 50 |
| Read pairs | 50 |
| R1 N-content | 100% |
| R2 N-content | 0% |
| Configured N-content threshold | 1% |
| Deterministic QC status | `FAIL` |
| QC flag | `R1_HIGH_N` |
| Structured finding | `HIGH_N_CONTENT` |
| Severity | `HIGH` |

The structured finding records the observed value and configured threshold. In the demonstrated run, the ML layer also flags `BAD` for review.

This example demonstrates that the deterministic rule identifies the known high N-content condition and that the ML layer can provide a separate anomaly signal.

It does not establish the sensitivity, specificity, or generalization performance of the ML model. The sample also has an unusually low read count, so its anomaly flag should not be attributed exclusively to N-content.

## 9. Version 2.0: ML Anomaly Detection

Version 2.0 extends the original rule-based workflow with unsupervised machine learning.

### Key additions

- Isolation Forest integration.
- Multiple QC metric features.
- Missing-value handling for ML input features.
- Anomaly scoring and review flags.
- Combined QC and ML output tables.
- Preservation of deterministic QC decisions.
- AI-assisted interpretation through the broader local-LLM workflow.

### How to interpret combined results

| Deterministic QC | ML assessment | Interpretation |
|---|---|---|
| PASS | No anomaly flag | No implemented rule failure or ML anomaly flag |
| PASS | Review | QC rules passed, but the metric pattern is unusual |
| FAIL | No anomaly flag | A QC rule failed, even if ML did not flag the sample |
| FAIL | Review | A rule failure and an unusual metric pattern warrant review |

ML flags do not replace the deterministic QC status or overwrite the original QC flags.

## 10. Project Structure

The following is a simplified representation of the repository:

```text
bioqc-agent/
├── config/
│   └── qc_thresholds.yaml
├── data/
│   ├── raw/
│   └── synthetic/
│       ├── README.md
│       ├── MANIFEST.tsv
│       ├── SYNTH_001_R1.fastq.gz
│       ├── SYNTH_001_R2.fastq.gz
│       ├── ...
│       ├── BAD_R1.fastq.gz
│       └── BAD_R2.fastq.gz
├── src/
│   ├── agent_input.py
│   ├── agent_prompt.py
│   ├── fastqc_parser.py
│   ├── llm_client.py
│   ├── qc_engine.py
│   ├── qc_interpreter.py
│   ├── qc_anomaly_detector.py
│   └── run_pipeline.py
├── results/
│   └── synthetic/
│       ├── sample_qc.tsv
│       ├── qc_findings.json
│       ├── qc_anomalies.tsv
│       └── fastqc/
├── .gitignore
└── README.md
```

This is an illustrative structure, not a guarantee that every listed file or directory exists in every checkout. Check the current repository and generated output when troubleshooting.

## 11. Configuration and Guardrails

QC thresholds are separated from the Python implementation in:

`config/qc_thresholds.yaml`

Keeping configuration separate makes it easier to inspect and adjust rule parameters.

The project follows these principles:

- Deterministic QC determines rule-based PASS/FAIL status.
- ML flags are separate from deterministic findings.
- The LLM explains the available evidence rather than replacing QC rules.
- AI-generated explanations require human review.
- Thresholds must be validated for the relevant assay, platform, sample type, and laboratory workflow.

BioQC-Agent is a research and portfolio prototype, not a validated clinical or laboratory QC system.

## 12. Current Status and Limitations

The project includes a deterministic QC engine, structured findings, Isolation Forest anomaly detection, and local LLM-assisted interpretation components.

The synthetic high-N test demonstrates a deterministic `FAIL` finding and an ML anomaly flag.

Limitations include:

- A small synthetic demonstration dataset.
- Synthetic sequences that are not biologically representative.
- A limited set of deterministic QC metrics.
- Q30 evaluation not yet implemented.
- ML assessments that depend on the analysed sample set.
- LLM interpretations that can vary and require review.
- No established real-world model performance evaluation.
- No validation as a clinical or laboratory QC system.

The end-to-end workflow should be tested against the current source code and dependencies before being described as fully operational in another environment.

## 13. Future Enhancements

Potential next steps include:

- Automated regression tests for QC rules.
- More comprehensive FastQC metric integration.
- Q30 and GC-content analysis.
- Sequence duplication assessment.
- MultiQC integration.
- Reproducible environment setup using Conda or Docker.
- HTML reports and QC visualizations.
- Audit logging and human approval workflows.
- Automated checks on AI-generated explanations.
- Evaluation on representative sequencing datasets.

## 14. Author

**Zarrine Raazi**

Bioinformatics | NGS | Genomics | Python | Machine Learning | AI-Assisted Bioinformatics

GitHub: https://github.com/zarrine905/bioqc-agent

## Project Philosophy

**Don't replace scientific rules with AI. Use AI to make scientific workflows easier to understand.**

BioQC-Agent explores a practical approach to responsible AI integration in bioinformatics: deterministic analysis, independent anomaly detection, transparent interpretation, and human oversight.
