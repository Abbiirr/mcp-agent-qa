from ollama import Client


def classify_action_via_llm(client: Client, action_text: str) -> str:
    """
    Use the LLM to classify the next action into one of: add data, do a curl, open a new account.
    """
    system_prompt = (
        "You are an action classification assistant. "
        "Given a user request, respond with exactly one of: 'add data', 'do a curl', or 'open a new account'."
    )
    response = client.chat(
        model="deepseek-r1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": action_text}
        ]
    )
    return response.message.content.strip().lower()