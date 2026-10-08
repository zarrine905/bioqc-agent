from openai import OpenAI

client = OpenAI()


def ask_llm(prompt):
    """Send a prompt to the OpenAI model and return its response."""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text


if __name__ == "__main__":
    result = ask_llm(
        "In one sentence, explain what FastQC does."
    )

    print(result)
