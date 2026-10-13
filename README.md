# BioQC-Agent: AI-Assisted NGS Quality Control

**Deterministic QC first. Machine learning second. AI-assisted interpretation third.**

BioQC-Agent is a Python-based bioinformatics project that combines FastQC, rule-based quality control, unsupervised machine learning, and a locally running large language model (LLM) to help researchers interpret next-generation sequencing (NGS) quality-control findings.

The project explores how AI can make sequencing QC easier to understand without replacing scientific rules or human review.

> **The rules decide. The ML model flags unusual patterns. The AI explains. The scientist decides.**

## 1. Project Overview

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
            +------------------+
            |                  |
            v                  v
   Structured Findings   QC Metrics for ML
                               |
                               v
                       Isolation Forest
                               |
                               v
                       Anomaly Assessment
            |                  |
            +---------+--------+
                      |
                      v
               AI Interpretation
                      |
                      v
             Ollama / Llama 3.2
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
- Isolation Forest-based anomaly detection.
- Sample-level QC summaries and ML assessment outputs.
- Local AI-assisted interpretation using Ollama and Llama 3.2 3B.
- Prompt constraints designed to reduce unsupported AI claims.
- Separation of deterministic QC status from ML anomaly flags.
- Synthetic FASTQ data for demonstration and testing.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Pipeline orchestration and QC logic |
| FastQC | Sequencing quality assessment |
| PyYAML | Reading QC configuration |
| pandas | QC tables and data processing |
| scikit-learn | Isolation Forest anomaly detection |
| Ollama | Local LLM runtime |
| Llama 3.2 3B | QC interpretation |
| JSON / TSV | Structured findings and reports |
| Git / GitHub | Version control and project hosting |

## 4. Available Test Data

A small synthetic paired-end FASTQ dataset is included in:

`data/synthetic/`

The directory contains ten paired-end sample datasets:

- `SYNTH_001_R1.fastq.gz` and `SYNTH_001_R2.fastq.gz`
- `SYNTH_002_R1.fastq.gz` and `SYNTH_002_R2.fastq.gz`
- `SYNTH_003_R1.fastq.gz` and `SYNTH_003_R2.fastq.gz`
- `SYNTH_004_R1.fastq.gz` and `SYNTH_004_R2.fastq.gz`
- `SYNTH_005_R1.fastq.gz` and `SYNTH_005_R2.fastq.gz`
- `SYNTH_006_R1.fastq.gz` and `SYNTH_006_R2.fastq.gz`
- `SYNTH_007_R1.fastq.gz` and `SYNTH_007_R2.fastq.gz`
- `SYNTH_008_R1.fastq.gz` and `SYNTH_008_R2.fastq.gz`
- `SYNTH_009_R1.fastq.gz` and `SYNTH_009_R2.fastq.gz`
- `SYNTH_010_R1.fastq.gz` and `SYNTH_010_R2.fastq.gz`

The dataset also contains:

- `README.md` — information about the synthetic data.
- `MANIFEST.tsv` — sample and dataset metadata.

These small files are intended for lightweight pipeline demonstrations, not biological inference or clinical validation.

The synthetic dataset contains no patient sequencing data.

## 5. Installation

BioQC-Agent is designed for Linux and has been developed in a Linux environment.

### Step 1: Clone the repository

```bash
git clone git@github.com:zarrine905/bioqc-agent.git
cd bioqc-agent
```

Alternatively, clone using HTTPS:

```bash
git clone https://github.com/zarrine905/bioqc-agent.git
cd bioqc-agent
```

### Step 2: Check Python

```bash
python3 --version
```

Python 3 is required.

### Step 3: Install Python dependencies

Install the core packages used by the QC and ML components:

```bash
python3 -m pip install pyyaml pandas scikit-learn
```

If you use a virtual environment, activate it before installing the packages.

### Step 4: Install FastQC

On Ubuntu or Debian:

```bash
sudo apt update
sudo apt install fastqc
```

Verify the installation:

```bash
fastqc --version
```

### Step 5: Install Ollama

Install Ollama using the official instructions:

https://ollama.com/download

Check that it is available:

```bash
ollama --version
```

### Step 6: Download the local model

BioQC-Agent is configured to use Llama 3.2 3B through Ollama.

```bash
ollama pull llama3.2:3b
```

Confirm that the model is available:

```bash
ollama list
```

You should see `llama3.2:3b` in the model list.

The local model avoids the need for an OpenAI API key or paid hosted-LLM API credits.

## 6. Run the End-to-End Pipeline

Run commands from the repository root, `bioqc-agent/`.

### Step 1: View the available options

```bash
python -m src.run_pipeline --help
```

The pipeline accepts options such as:

- `--data-dir` — input FASTQ directory.
- `--output` — output directory.
- `--fastqc-dir` — FastQC output directory.
- `--config` — QC configuration file.

### Step 2: Run on the included synthetic data

```bash
python -m src.run_pipeline --data-dir data/synthetic/
```

To explicitly specify the output directory:

```bash
python -m src.run_pipeline \
  --data-dir data/synthetic/ \
  --output results/synthetic
```

**Important:** Use `python -m src.run_pipeline` from the repository root. Running `python src/run_pipeline.py` may cause import errors because the code imports modules through the `src` package.

### Step 3: Inspect the results

List the generated files:

```bash
find results -maxdepth 3 -type f | sort
```

Inspect the sample summary, if generated at this path:

```bash
cat results/synthetic/sample_qc_summary.tsv
```

Inspect structured QC findings:

```bash
cat results/synthetic/qc_findings.json
```

The exact outputs depend on the current runner configuration. Use the files generated by your run as the authoritative record.

## 7. Understanding the QC Results

BioQC-Agent separates three types of assessment.

### A. Deterministic QC

The Python QC engine applies configured rules to supported metrics.

Examples include:

- N-content threshold evaluation.
- Adapter-content threshold evaluation.

The configured thresholds are stored in:

`config/qc_thresholds.yaml`

The current configuration includes N-content and adapter-content thresholds, as well as a Q30 configuration value for future use. Q30 evaluation is not currently implemented.

### B. Machine Learning Anomaly Detection

Version 2.0 adds an Isolation Forest model to identify samples with unusual combinations of QC metrics.

The intended feature set includes:

- Total reads in millions.
- R1 N-content.
- R2 N-content.
- R1 adapter content.
- R2 adapter content.

The ML layer can produce an anomaly score, an anomaly flag, and a review assessment.

An anomaly score is not a probability of sequencing failure. A sample can pass deterministic QC and still be flagged by the ML model.

### C. AI-Assisted Interpretation

The local LLM receives structured QC findings and generates explanations and relevant follow-up checks.

For example, a high N-content finding may prompt a reviewer to investigate read quality, base-calling performance, or the sequencing run's QC metrics.

These are possible investigation steps, not proof of the cause of the finding.

The AI layer is intended to explain available evidence rather than independently determine whether a sample passes QC.

## 8. Version 2.0: Machine Learning Anomaly Detection

Version 2.0 extends the original rule-based QC workflow with unsupervised machine learning.

### What changed in Version 2.0?

1. **Isolation Forest integration**  
   Adds an unsupervised ML approach for identifying unusual QC metric patterns.

2. **Multiple QC features**  
   Uses a feature set covering total reads, R1/R2 N-content, and R1/R2 adapter content.

3. **Missing-value handling**  
   Supports median imputation where appropriate for the ML input features.

4. **Anomaly scoring**  
   Produces anomaly scores and review flags for samples.

5. **Combined QC and ML outputs**  
   Makes it possible to inspect deterministic QC results alongside ML assessments.

6. **Preserved QC decisions**  
   ML flags do not replace the deterministic QC status or overwrite the original QC flags.

7. **AI-assisted explanation**  
   The broader BioQC-Agent workflow uses structured findings to support local LLM-based interpretation.

### How to interpret an ML flag

| Deterministic QC | ML assessment | Interpretation |
|---|---|---|
| PASS | No anomaly flag | No implemented rule failure or ML anomaly flag |
| PASS | Review | QC rules passed, but the sample has an unusual metric pattern |
| FAIL | No anomaly flag | At least one QC rule failed, even if ML did not flag the sample |
| FAIL | Review | A rule failure and an unusual metric pattern both warrant review |

The ML model is fitted to the analysed sample set, so its assessments depend on dataset composition, preprocessing, and model settings.

ML flags should be reviewed alongside deterministic findings and relevant assay-specific requirements.

## 9. Project Structure

The following is a simplified view of the repository. Generated output files may vary depending on the run and configuration.

```text
bioqc-agent/
├── config/
│   └── qc_thresholds.yaml
│
├── data/
│   ├── raw/
│   └── synthetic/
│       ├── README.md
│       ├── MANIFEST.tsv
│       ├── SYNTH_001_R1.fastq.gz
│       ├── SYNTH_001_R2.fastq.gz
│       ├── ...
│       ├── SYNTH_010_R1.fastq.gz
│       └── SYNTH_010_R2.fastq.gz
│
├── src/
│   ├── agent_input.py
│   ├── agent_prompt.py
│   ├── fastqc_parser.py
│   ├── llm_client.py
│   ├── qc_engine.py
│   ├── qc_interpreter.py
│   ├── qc_anomaly_detector.py
│   └── run_pipeline.py
│
├── results/
│   └── synthetic/
│       ├── sample_qc_summary.tsv
│       ├── qc_findings.json
│       └── ...
│
├── .gitignore
└── README.md
```

This diagram describes the intended organization. Confirm the exact module names and generated output paths against the current repository before relying on the diagram as a complete file inventory.

## 10. QC Configuration and Guardrails

Thresholds are separated from the Python implementation in:

`config/qc_thresholds.yaml`

Keeping configuration separate makes it easier to inspect and modify the rule parameters.

These thresholds are project settings, not universal scientific standards. A production workflow would need thresholds validated for its sequencing platform, assay, sample type, and laboratory requirements.

The AI layer is designed with the following constraints:

- Deterministic QC determines rule-based PASS/FAIL status.
- The LLM is instructed not to modify QC thresholds.
- Structured findings are provided as evidence for interpretation.
- ML anomaly flags remain separate from deterministic QC decisions.
- AI-generated explanations and recommendations require human review.

Prompt constraints reduce the risk of unsupported output but cannot guarantee that an LLM will never produce an inaccurate statement.

## 11. Current Status and Limitations

BioQC-Agent is a portfolio and research prototype.

Its intended capabilities include paired-end FASTQ discovery, FastQC execution, configured N-content and adapter-content rules, structured findings, ML anomaly detection, and local LLM-assisted interpretation.

The complete workflow should be validated against the current code and a successful end-to-end run before being described as fully operational.

Current limitations include:

- A small synthetic demonstration dataset.
- A limited set of deterministic QC metrics.
- Q30 evaluation not yet implemented.
- No integrated MultiQC requirement in the main pipeline.
- ML assessments that depend on the analysed sample set.
- LLM interpretations that can vary and require review.
- No validation as a clinical or laboratory QC system.

The project should not replace a validated laboratory workflow or the judgement of a qualified bioinformatics reviewer.

## 12. Future Enhancements

Potential next steps include:

- MultiQC integration.
- Additional FastQC metric checks.
- Q30 and GC-content analysis.
- Sequence duplication assessment.
- Automated tests for individual QC rules.
- Reproducible environment setup using Conda or Docker.
- HTML reports and QC visualizations.
- Audit logging and human approval workflows.
- Improved validation of AI-generated output.
- Evaluation against representative sequencing datasets.

## 13. Author

**Zarrine Raazi**

Bioinformatics | NGS | Genomics | Python | Machine Learning | AI-Assisted Bioinformatics

GitHub: https://github.com/zarrine905/bioqc-agent

## Project Philosophy

Don't replace scientific rules with AI. Use AI to make scientific workflows easier to understand.

**BioQC-Agent explores a practical approach to responsible AI integration in bioinformatics: deterministic analysis, independent anomaly detection, transparent interpretation, and human oversight.**
