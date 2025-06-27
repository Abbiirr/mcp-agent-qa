import requests
from config import settings
# Fixed import syntax - Python uses dots for module paths, not file paths with slashes
from schemas.schemas import InsertCredentialsRequest
from pydantic import ValidationError
from ollama import Client


def handle_add_data(client: Client, project: str):
    """
    Stub for adding data to the specified project.
    """
    print(f"Adding data for project {project}...")
    # TODO: implement actual data insertion logic here


def handle_do_curl(client: Client, project: str):
    """
    Stub for executing a CURL command for the specified project.
    """
    print(f"Executing CURL operations for project {project}...")
    # TODO: implement actual HTTP request logic here


def handle_open_new_account(client: Client, project: str):
    """
    Use the MCP-defined insert_user function to open a new account in the database.
    Prompts the user for account details, validates against the schema, and invokes the MCP server.
    """
    print(f"Opening a new account for project {project}...")
    # Collect user data
    user_id = input("Enter user_id: ")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email (optional): ") or None
    phone = input("Enter phone number (optional): ") or None
    # Default to active
    is_active_input = input("Is the account active? (y/n) [y]: ") or "y"
    is_active = is_active_input.strip().lower() not in ["n", "no"]

    # Prepare payload
    payload = {
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone_number": phone,
        "is_active": is_active,
    }

    # Validate payload
    try:
        InsertCredentialsRequest(**payload)
    except ValidationError as e:
        print("Validation error:\n", e)
        return

    # Call the MCP server's HTTP endpoint
    url = settings.MCP_ENDPOINT if hasattr(settings, 'MCP_ENDPOINT') else "http://localhost:8000/insert_user"
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        new_id = data.get("inserted_id")
        print(f"✅ New account created with id: {new_id}")
    except requests.RequestException as err:
        print(f"❌ Failed to create account: {err}")