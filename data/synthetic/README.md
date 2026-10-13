# Synthetic FASTQ Test Data

This directory contains 10 artificial paired-end FASTQ samples for testing BioQC-Agent. No real participant or research sequencing reads are included.

## Dataset

- 10 samples: SYNTH_001 through SYNTH_009, plus BAD
- 50 read pairs per sample
- Read length: 100 bases
- Baseline samples contain artificial random A/C/G/T sequences and uniform quality characters.
- BAD_R1.fastq.gz is intentionally degraded: every base in each R1 sequence is N, giving 100% R1 N-content.
- BAD_R2.fastq.gz is the paired R2 file.

## Expected QC result for BAD

With the configured N-content threshold of 1%:

- Status: FAIL
- QC flag: R1_HIGH_N
- Finding: HIGH_N_CONTENT
- Observed R1 N-content: 100%

The ML anomaly detector may additionally flag BAD for review. ML screening supplements, rather than replaces, deterministic QC rules.

## Limitations

These artificial sequences are for software testing only. They are not biologically representative and must not be used to validate real-world sequencing QC performance.
