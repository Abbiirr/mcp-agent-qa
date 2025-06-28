from ollama import Client


def classify_project_via_llm(client: Client, project_text: str) -> str:
    """
    Use the LLM to classify project into one of: Gigly, NCC, MMBL, UCB.
    """
    system_prompt = (
        "You are a project classification assistant. "
        "Given a project name or description, respond with exactly one of: "
        "'Gigly', 'NCC', 'MMBL', or 'UCB'."
    )
    response = client.chat(
        model="deepseek-r1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": project_text}
        ]
    )
    return response.message.content.strip().title()