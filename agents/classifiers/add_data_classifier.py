# agents/classifiers/add_data_classifier.py

from ollama import Client
from agents.actions.pathao_data_add import handle_pathao_data
from agents.actions.uber_data_add import handle_uber_data

def handle_add_data(client: Client, project: str):
    """
    Adds data to the specified project by asking which service to use:
    'pathao' or 'uber', then delegating to the appropriate handler.
    """
    print(f"\n📥 Adding data for project '{project}'…\n")

    # 1) Prompt for service type
    service = input("Which service? (pathao/uber): ").strip().lower()
    if service == "pathao":
        handle_pathao_data(client, project)
    elif service == "uber":
        handle_uber_data(client, project)
    else:
        print(f"❌ Unknown service '{service}'. Please choose either 'pathao' or 'uber'.\n")