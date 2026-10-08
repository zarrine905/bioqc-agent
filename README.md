# 🧬 BioQC-Agent

### AI-assisted QC for NGS — deterministic first, intelligent second.

**BioQC-Agent** is a lightweight bioinformatics project that combines **FastQC + Python + a local LLM** to turn sequencing QC findings into clear, human-readable interpretations.

> **The rules decide. The AI explains. The scientist decides.**

---

### 🔬 What it does

**FASTQ → FastQC → Python QC Engine → Structured Findings → Local AI → QC Interpretation**

- ⚙️ Deterministic QC using Python
- 🧪 FastQC-based sequencing assessment
- 📊 Structured QC findings
- 🤖 Local **Llama 3.2 3B** through Ollama
- 🛡️ Guardrails to prevent invented metrics or changed thresholds
- 👩‍🔬 Human-in-the-loop scientific review

---

### 🧠 Why this project?

Traditional QC tools produce measurements.  
BioQC-Agent explores how AI can help **interpret those measurements without replacing the underlying scientific rules**.

The LLM does **not** decide whether a sample passes QC.

It receives validated findings and helps answer:

**“What does this QC finding mean, and what should I check next?”**

---

### ✨ Key principle

**Deterministic analysis → AI interpretation → Human decision**

This separation makes the workflow more **transparent, auditable, and safer for scientific use**.

---

### 🛠️ Built With

**Python · FastQC · YAML · JSON · Ollama · Llama 3.2 · Linux · Git**

---

### 🚀 Current Status

**Working prototype**

Currently supports N-content and adapter-content QC with automated PASS/FAIL evaluation and local AI interpretation.

Future direction: richer QC metrics, MultiQC integration, visualization, testing, and human-approval workflows.

---

### 👩‍💻 Author

**Zarrine Raazi**  
Bioinformatics • NGS • Genomics • Python • AI-assisted Bioinformatics

⭐ *Built as a portfolio project exploring practical and responsible AI integration in bioinformatics.*
