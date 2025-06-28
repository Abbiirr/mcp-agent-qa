from ollama import Client


def classify_action_via_llm(client, action_input):
    """
    Use the LLM to classify the user action into one of the predefined categories.
    Returns just the classified action without any thinking text.
    """
    # Your existing code that calls the LLM
    response = client.chat(
        model="deepseek-r1:8b",
        messages=[
            {
                "role": "system",
                "content": "You are an action classifier. Classify the user's request into exactly one of these categories: 'add data', 'do a curl', or 'open a new account'."
            },
            {
                "role": "user",
                "content": action_input
            }
        ]
    )

    raw_response = response['message']['content']

    # Extract the actual classification from the response
    # If it contains thinking tags, get only the text after all tags
    if '<think>' in raw_response and '</think>' in raw_response:
        # Get the text after the last </think> tag
        action = raw_response.split('</think>')[-1].strip()
    else:
        action = raw_response.strip()

    # Further clean up the response to match expected actions exactly
    for expected_action in ['add data', 'do a curl', 'open a new account']:
        if expected_action in action.lower():
            return expected_action

    # Default fallback
    return action.lower()