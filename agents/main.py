from client import get_ollama_client
from intent_classifier import classify_intent_via_llm
from project_classifier import classify_project_via_llm
from ollama import ResponseError


def main():
    # Initialize Ollama client
    try:
        client = get_ollama_client()
    except RuntimeError as err:
        print(err)
        return

    # Step 1: Ask and classify intent
    user_input = input("Hello, Friday! 🤖\nWhat do you want to do today?\n>>")
    try:
        intent = classify_intent_via_llm(client, user_input)
        print(f"👉 Detected intent: {intent}")
    except ResponseError as err:
        print(f"Ollama error ({err.status_code}): {err.error}")
        return

    # Step 2: Ask and classify project
    project_input = input("Which project would you like to work on?\n>>")
    try:
        project = classify_project_via_llm(client, project_input)
        print(f"🎯 You chose to do **{intent}** on project **{project}**.")
    except ResponseError as err:
        print(f"Ollama error ({err.status_code}): {err.error}")

if __name__ == "__main__":
    main()