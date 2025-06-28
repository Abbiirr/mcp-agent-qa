from client import get_ollama_client
from agents.classifiers.intent_classifier import classify_intent_via_llm
from agents.classifiers.project_classifier import classify_project_via_llm
from agents.classifiers.action_classifier import classify_action_via_llm
from agents.common_actions import (
    handle_add_data,
    handle_do_curl,
    handle_open_new_account
)
from agents.actions.auth import login_and_get_token
from ollama import ResponseError
from agents.actions.pathao_data_add import (
handle_full_trip_data,

)
from agents.classifiers.pathao_intent_classifier import handle_pathao_data
from agents.actions.pathao_data_add import (
handle_ride_request_data,
)


def main():
    auth_token = None
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

    # auth_token = login_and_get_token()
    auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEiLCJleHAiOjE3NTEwOTQzNzl9.U0UAmv84ii_yckpsz578r45czyaymUw_LLXyVRXFTxU"
    # handle_pathao_data(client, "project", auth_token)
    handle_ride_request_data(client, "project", auth_token)

if __name__ == "__main__":
    main()