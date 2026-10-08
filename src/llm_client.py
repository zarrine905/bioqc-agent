import subprocess


MODEL = "llama3.2:3b"


def ask_llm(prompt):
    """Send a prompt to the local Ollama model and return its response."""

    result = subprocess.run(
        ["ollama", "run", MODEL, prompt],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


if __name__ == "__main__":
    result = ask_llm(
        "In one sentence, explain what FastQC does."
    )

    print(result)
