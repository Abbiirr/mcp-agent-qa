from ollama import Client


def classify_intent_via_llm(client: Client, user_text: str) -> str:
    """
    Use the LLM to classify intent into 'api testing' or 'front end testing'.
    """
    system_prompt = (
        "You are an intent classification assistant. "
        "When given a request, respond with exactly one of: "
        "'api testing' or 'front end testing'."
    )
    response = client.chat(
        model="deepseek-r1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    )
    return response.message.content.strip().lower()