import gzip
import random
from pathlib import Path

OUT = Path("data/synthetic")
OUT.mkdir(parents=True, exist_ok=True)

rng = random.Random(20261013)
bases = "ACGT"
read_length = 100
reads_per_sample = 50
samples = 10

for sample_num in range(1, samples + 1):
    sample = f"SYNTH_{sample_num:03d}"

    r1_path = OUT / f"{sample}_R1.fastq.gz"
    r2_path = OUT / f"{sample}_R2.fastq.gz"

    with gzip.open(r1_path, "wt", encoding="ascii") as r1, \
         gzip.open(r2_path, "wt", encoding="ascii") as r2:

        for read_num in range(1, reads_per_sample + 1):
            seq1 = "".join(rng.choices(bases, k=read_length))
            seq2 = "".join(rng.choices(bases, k=read_length))
            quality = "I" * read_length

            header1 = f"@{sample}:SYNTHETIC:READ{read_num:04d}/1"
            header2 = f"@{sample}:SYNTHETIC:READ{read_num:04d}/2"

            r1.write(f"{header1}\n{seq1}\n+\n{quality}\n")
            r2.write(f"{header2}\n{seq2}\n+\n{quality}\n")

manifest = OUT / "MANIFEST.tsv"
with manifest.open("w", encoding="utf-8") as f:
    f.write("sample_id\tread1\tread2\tdata_type\n")
    for i in range(1, samples + 1):
        sample = f"SYNTH_{i:03d}"
        f.write(
            f"{sample}\t{sample}_R1.fastq.gz\t"
            f"{sample}_R2.fastq.gz\t"
            "fully_synthetic_random_sequences\n"
        )

(OUT / "README.md").write_text(
    "# Synthetic FASTQ Test Data\n\n"
    "This directory contains 10 artificial paired-end FASTQ samples "
    "generated using Python's standard library.\n\n"
    "- 10 samples, with R1 and R2 files per sample\n"
    "- 50 read pairs per sample\n"
    "- Read length: 100 bases\n"
    "- Random A/C/G/T sequences and uniform quality characters\n"
    "- No real participant or research sequencing reads are included\n\n"
    "**Limitations:** These random sequences are for software testing "
    "only. They are not biologically representative and should not be "
    "used to validate real-world sequencing QC performance.\n",
    encoding="utf-8",
)

print(f"Created {samples} synthetic paired-end samples in {OUT}")
print(f"FASTQ files: {samples * 2}")
print(f"Read pairs per sample: {reads_per_sample}")
