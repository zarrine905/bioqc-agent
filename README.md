# 🧬 BioQC-Agent

### AI-assisted QC for NGS — deterministic first, intelligent second.

**BioQC-Agent** is a lightweight bioinformatics project that combines **FastQC + Python + a local LLM** to turn sequencing QC findings into clear, human-readable interpretations.

> **The rules decide. The AI explains. The scientist decides.**

---

## 🔬 What It Does

**FASTQ → FastQC → Python QC Engine → Structured Findings → Local AI → QC Interpretation**

- ⚙️ Deterministic QC using Python
- 🧪 FastQC-based sequencing assessment
- 📊 Structured QC findings
- 🤖 Local **Llama 3.2 3B** through Ollama
- 🛡️ Guardrails to prevent invented metrics or changed thresholds
- 👩‍🔬 Human-in-the-loop scientific review

---

## 🧠 Why This Project?

Traditional QC tools produce measurements, but interpreting those findings can still involve manual review.

BioQC-Agent explores how AI can help **interpret QC results without replacing the underlying scientific rules**.

The LLM does **not** decide whether a sample passes QC.

Instead, it receives deterministic findings and helps answer:

> **“What does this QC finding mean, and what should I check next?”**

---

## ✨ Key Principle

**Deterministic analysis → AI interpretation → Human decision**

The Python QC engine is the source of truth.

The LLM:

- Does not calculate or modify QC measurements
- Does not change configured thresholds
- Does not determine PASS/FAIL
- Does not invent QC results
- Provides explanations and relevant QC checks

Final scientific decisions remain with the appropriate bioinformatics or scientific reviewer.

---

## 🛠️ Built With

**Python · FastQC · YAML · JSON · Ollama · Llama 3.2 · Linux · Git**

---

# 🚀 Getting Started

## 🧰 Prerequisites

BioQC-Agent is designed to run on Linux.

You will need:

- **Python 3**
- **Git**
- **FastQC**
- **Ollama**
- **Llama 3.2 3B**

You do **not** need an OpenAI API key or paid LLM credits. The AI interpretation runs locally through Ollama.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone git@github.com:zarrine905/bioqc-agent.git
cd bioqc-agent
```

### 2. Check Python

```bash
python3 --version
```

### 3. Install the Python dependency

BioQC-Agent currently uses `PyYAML` for reading the QC configuration.

```bash
python3 -m pip install pyyaml
```

### 4. Install FastQC

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install fastqc
```

Check that FastQC is available:

```bash
fastqc --version
```

### 5. Install Ollama

Install Ollama for your operating system.

Then check:

```bash
ollama --version
```

### 6. Download the local LLM

BioQC-Agent uses **Llama 3.2 3B** through Ollama:

```bash
ollama pull llama3.2:3b
```

Check that the model is available:

```bash
ollama list
```

You should see:

```text
llama3.2:3b
```

---

# 🧪 Included Test Dataset

You don't need your own sequencing data to try the project.

A small **synthetic paired-end FASTQ dataset** is included in:

`data/test/`

It contains two sample cases:

| Sample | Purpose | Expected Result |
|---|---|---|
| `SAMPLE01` | Clean example | ✅ PASS |
| `BAD01` | Intentionally high N-content in R1 | ❌ FAIL |

`BAD01` contains a read with N bases in R1, resulting in **25% N-content**.

The configured N-content threshold is **1%**, so the deterministic QC engine flags the sample:

**25% > 1% → FAIL**

This gives a first-time visitor a simple example of both a passing and failing QC result.

> The dataset is synthetic and intended only for demonstration and testing. No patient or clinical sequencing data is included.

---

# ▶️ Run the Pipeline

Once the prerequisites are installed, run:

```bash
python -m src.run_pipeline
```

That's all you need for the first demonstration.

The pipeline automatically performs:

**FASTQ → FastQC → Deterministic QC → Structured Findings → Local LLM → AI Interpretation**

You do **not** need to manually start the Llama model before running the pipeline.

---

## 📊 What Happens During the Run?

### 1. FastQC

FastQC analyzes the FASTQ files and generates QC reports.

### 2. Deterministic QC

The Python QC engine extracts selected metrics and applies the configured QC rules.

### 3. Structured Findings

Detected problems are converted into structured JSON findings.

### 4. AI Interpretation

The findings are passed to a guarded prompt and interpreted by the local **Llama 3.2 3B** model.

### 5. Report

The AI interpretation is saved as a text report.

---

# 📁 Results

After the pipeline finishes, look inside the `results/` directory.

| File | Purpose |
|---|---|
| `sample_qc.tsv` | Sample-level QC measurements and PASS/FAIL status |
| `qc_findings.json` | Structured QC findings |
| `ai_qc_interpretation.txt` | AI-generated QC interpretation |
| `fastqc/` | FastQC reports |

For the included dataset, you should see approximately:

**SAMPLE01 → PASS** ✅

**BAD01 → FAIL — HIGH_N_CONTENT (R1)** ❌

---

# 🏗️ Architecture

```text
                    FASTQ Files
                         │
                         ▼
                       FastQC
                         │
                         ▼
                FastQC Result Parser
                         │
                         ▼
               Python QC Engine
                         │
                 ┌───────┴───────┐
                 ▼               ▼
          sample_qc.tsv    qc_findings.json
                                 │
                                 ▼
                           Agent Input
                                 │
                                 ▼
                        Guarded AI Prompt
                                 │
                                 ▼
                       Ollama / Llama 3.2
                                 │
                                 ▼
                    AI QC Interpretation
                                 │
                                 ▼
                 ai_qc_interpretation.txt
```

---

# 🧬 QC Configuration

QC thresholds are kept separately in:

`config/qc_thresholds.yaml`

This keeps configuration separate from the Python logic.

Current configuration includes:

- N-content threshold
- Adapter-content threshold
- Q30 configuration for future use

The current implementation evaluates **N-content and adapter-content**.

> These thresholds are configurable project parameters, not universal scientific standards. Production use would require validation against the relevant sequencing platform, assay, and laboratory QC requirements.

---

# 🛡️ AI Guardrails

The AI layer is intentionally limited.

### Deterministic QC is authoritative

PASS/FAIL is determined by Python rules before the LLM is called.

### No threshold changes

The LLM is instructed to use the configured threshold and not modify it.

### No invented measurements

The model only receives the measurements produced by the deterministic QC engine.

### Findings are separated from measurements

For example:

**Finding:** `HIGH_N_CONTENT`

**Observed:** `25.0`

The finding label is not treated as a measurement.

### Recommendations stay within scope

The model is instructed to recommend checks related to the detected QC finding rather than inventing unsupported causes.

### Human review remains important

The AI output is an interpretation aid, not a replacement for scientific review.

---

# 🧬 Using Your Own FASTQ Data

After confirming that the included example works, the pipeline can be adapted for your own paired-end FASTQ files.

The expected naming convention is:

`SAMPLE_R1.fastq.gz`

`SAMPLE_R2.fastq.gz`

For example:

`Sample01_R1.fastq.gz`

`Sample01_R2.fastq.gz`

It is recommended to test the included synthetic dataset first so you can confirm that **FastQC, the Python QC engine, and the local LLM are working correctly** before introducing real sequencing data.

---

# 📂 Project Structure

```text
bioqc-agent/
│
├── config/
│   └── qc_thresholds.yaml
│
├── data/
│   ├── raw/
│   └── test/
│
├── src/
│   ├── agent_input.py
│   ├── agent_prompt.py
│   ├── fastqc_parser.py
│   ├── llm_client.py
│   ├── qc_engine.py
│   ├── qc_interpreter.py
│   └── run_pipeline.py
│
├── .gitignore
└── README.md
```

Generated results and sequencing data are excluded from Git tracking.

---

# 🚧 Current Status

### Working prototype

Currently supports:

- FASTQ paired-end sample discovery
- FastQC execution
- N-content evaluation
- Adapter-content evaluation
- Configurable QC thresholds
- Deterministic PASS/FAIL evaluation
- Structured QC findings
- Local LLM integration
- Guarded AI interpretation
- Automated end-to-end execution

---

# 🔮 Future Enhancements

The project is intentionally starting small.

Possible next steps include:

- MultiQC integration
- Additional FastQC metrics
- Q30 analysis
- GC-content analysis
- Sequence duplication analysis
- Automated testing
- Docker/Conda environment
- HTML QC + AI reports
- QC visualization
- Batch processing
- Human approval workflow
- Audit logging
- Additional sequencing platform support
- More robust LLM output validation

**MultiQC is not currently a required dependency because it is not yet part of the automated pipeline.**

---

# ⚠️ Limitations

BioQC-Agent is a **portfolio/research prototype** and is not intended to replace a validated clinical or laboratory QC workflow.

Current limitations include:

- Limited QC metrics
- Small synthetic test dataset
- Limited validation across sequencing platforms
- LLM output may vary between runs
- AI recommendations require human review
- QC thresholds require assay/platform-specific validation
- Q30 evaluation is not currently implemented
- MultiQC is not yet integrated into the main runner

---

# 👩‍💻 Author

### Zarrine Raazi

**Bioinformatics • NGS • Genomics • Python • AI-assisted Bioinformatics**

⭐ Built as a portfolio project exploring practical and responsible AI integration in bioinformatics.

---

## 📌 Project Philosophy

> **Don't replace scientific rules with AI. Use AI to make scientific workflows easier to understand.**

---

# 🤖 Version 2.0 — Machine Learning Anomaly Detection

BioQC-Agent v2.0 extends deterministic sequencing QC with **unsupervised machine learning** to identify samples that may warrant additional review.

The new ML layer uses **Isolation Forest** from scikit-learn to flag samples with unusual combinations of QC metrics.

## What’s New in v2.0?

- **ML-based anomaly detection** using Isolation Forest.
- **Five QC metrics:** total million reads, R1 and R2 N-content, and R1 and R2 adapter content.
- **Missing-value handling** using median imputation where appropriate.
- **Anomaly scores and review flags** in a tab-separated output file.
- **Combined QC and ML findings** for downstream interpretation.
- **Preserved deterministic decisions:** ML flags do not overwrite the original QC status or flags.

## How the Three Layers Work

1. **Deterministic QC:** applies configured thresholds and assigns PASS or FAIL.
2. **ML anomaly detection:** identifies unusual samples relative to the samples analysed together.
3. **AI-assisted interpretation:** helps communicate the available QC evidence and relevant follow-up checks.

> An anomaly flag is a signal for review, not proof of a sequencing error. A sample can pass deterministic QC and still be flagged by ML.

## Run the ML Demonstration

Install the required Python packages:

```bash
python3 -m pip install pyyaml pandas scikit-learn
```

Run the demonstration:

```bash
python -m src.qc_anomaly_detector --demo
```

This creates artificial QC data containing an intentionally unusual sample. It does not require real sequencing data.

### Output files

| File | Purpose |
|---|---|
| `results/demo_sample_qc.tsv` | Artificial input data for the demo |
| `results/qc_anomalies.tsv` | QC metrics, anomaly scores, review flags, and explanations |

Inspect the results:

```bash
python - <<'PY'
import pandas as pd

df = pd.read_csv("results/qc_anomalies.tsv", sep="\t")

columns = [
    "Sample",
    "QC_status",
    "ML_anomaly_score",
    "ML_assessment",
    "ML_explanation",
]

print(df[columns].to_string(index=False))
PY
```

## Run ML on Existing QC Results

If `results/sample_qc.tsv` contains the required metrics and enough usable samples, run:

```bash
python -m src.qc_anomaly_detector
```

The detector writes its output to `results/qc_anomalies.tsv` by default.

The demonstration requires at least five usable samples. Ten or more representative samples are preferable, but results remain dependent on dataset composition and model settings.

## Interpreting the Results

- `ML_anomaly_score`: higher values indicate more unusual observations according to the fitted model.
- `ML_anomaly`: whether Isolation Forest flagged the sample.
- `ML_assessment`: `REVIEW` or `NO_ANOMALY_FLAG`.
- `ML_explanation`: a short explanation based on selected metric checks.

The model's anomaly score is not a probability of failure. Its flags should be reviewed alongside the underlying metrics, deterministic QC findings, and relevant assay requirements.

## Limitations

This is an experimental portfolio project, not a validated clinical QC system. The ML detector requires further evaluation on representative sequencing datasets, including assessment of false positives, false negatives, and performance across sequencing platforms.

The included demo data are artificial and must not be interpreted as evidence of real-world model performance.

---

**Version:** 2.0  
**Focus:** NGS quality control, unsupervised machine learning, and responsible AI-assisted interpretation.
