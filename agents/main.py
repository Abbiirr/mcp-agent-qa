from client import get_ollama_client
from intent_classifier import classify_intent_via_llm
from project_classifier import classify_project_via_llm
from action_classifier import classify_action_via_llm
from actions import (
    handle_add_data,
    handle_do_curl,
    handle_open_new_account
)
from ollama import ResponseError


def main():
    # Initialize Ollama client
    try:
        client = get_ollama_client()
    except RuntimeError as err:
        print(err)
        return

    # # Step 1: Ask and classify intent
    # user_input = input("Hello, Friday! 🤖\nWhat do you want to do today?\n>>")
    # try:
    #     intent = classify_intent_via_llm(client, user_input)
    #     print(f"👉 Detected intent: {intent}")
    # except ResponseError as err:
    #     print(f"Ollama error ({err.status_code}): {err.error}")
    #     return
    #
    # # Step 2: Ask and classify project
    # project_input = input("Which project would you like to work on?\n>>")
    # try:
    #     project = classify_project_via_llm(client, project_input)
    #     print(f"🎯 You chose to do **{intent}** on project **{project}**.")
    # except ResponseError as err:
    #     print(f"Ollama error ({err.status_code}): {err.error}")
    #
    # # Step 3: Classify action
    # action_input = input(
    #     "What would you like to do first? (add data, do a curl, open a new account)\n>>"
    # )
    # try:
    #     action = classify_action_via_llm(client, action_input)
    #     print(f"🚀 Next action: {action}")
    # except ResponseError as err:
    #     print(f"Ollama error ({err.status_code}): {err.error}")
    #     return
    #
    # # Step 4: Execute chosen action
    # if action == "add data":
    #     handle_add_data(client, project)
    # elif action == "do a curl":
    #     handle_do_curl(client, project)
    # elif action == "open a new account":
    #     handle_open_new_account(client, project)
    # else:
    #     print(f"Unknown action: {action}")

    handle_open_new_account(client, "gigly")

if __name__ == "__main__":
    main()