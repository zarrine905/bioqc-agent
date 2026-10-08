from pathlib import Path
import zipfile


def get_fastqc_data(fastqc_zip):
    """Extract fastqc_data.txt from a FastQC ZIP file."""

    fastqc_zip = Path(fastqc_zip)

    with zipfile.ZipFile(fastqc_zip, "r") as z:
        for filename in z.namelist():
            if filename.endswith("fastqc_data.txt"):
                return z.read(filename).decode("utf-8")

    raise FileNotFoundError(
        f"fastqc_data.txt not found in {fastqc_zip}"
    )


def calculate_n_content(fastqc_text):
    """Return maximum N content percentage across positions."""

    lines = fastqc_text.splitlines()
    in_module = False
    n_values = []

    for line in lines:

        if line.startswith(">>Per base N content"):
            in_module = True
            continue

        if in_module and line.startswith(">>END_MODULE"):
            break

        if in_module and line and not line.startswith("#"):
            parts = line.split()

            if len(parts) >= 2:
                n_values.append(float(parts[1]))

    if not n_values:
        return 0.0

    return max(n_values)


def calculate_adapter_content(fastqc_text):
    """Return maximum adapter contamination percentage."""

    lines = fastqc_text.splitlines()
    in_module = False
    adapter_values = []

    for line in lines:

        if line.startswith(">>Adapter Content"):
            in_module = True
            continue

        if in_module and line.startswith(">>END_MODULE"):
            break

        if in_module and line and not line.startswith("#"):
            parts = line.split()

            if len(parts) >= 2:
                for value in parts[1:]:
                    adapter_values.append(float(value))

    if not adapter_values:
        return 0.0

    return max(adapter_values)


def parse_fastqc(fastqc_zip):
    """Return sample-level metrics from a FastQC ZIP."""

    text = get_fastqc_data(fastqc_zip)

    return {
        "N_percent": calculate_n_content(text),
        "Adapter_percent": calculate_adapter_content(text),
        }
