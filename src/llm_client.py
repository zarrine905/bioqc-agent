import re
import subprocess
import subprocess

MODEL = "llama3.2:3b"
TIMEOUT_SECONDS = 180


def ask_llm(prompt):
    """Send a prompt to Ollama with a timeout and useful error messages."""

    try:
        result = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            capture_output=True,
            text=True,
            check=True,
            timeout=TIMEOUT_SECONDS,
        )

    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Ollama did not finish within {TIMEOUT_SECONDS} seconds. "
            "Try a shorter prompt or check model performance."
        ) from exc

    except subprocess.CalledProcessError as exc:
        error = (exc.stderr or "").strip()
        raise RuntimeError(
            f"Ollama returned an error: {error or exc.returncode}"
        ) from exc

    response = result.stdout

    # Remove ANSI escape sequences and terminal control characters.
    response = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", response)
    response = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", response)
    response = response.strip()
    if not response:
        raise RuntimeError("Ollama returned an empty response.")

    return response


if __name__ == "__main__":
    result = ask_llm(
        "In one sentence, explain what FastQC does."
    )
    print(result)
