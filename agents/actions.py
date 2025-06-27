import requests
from config import settings
from schemas.schemas import InsertCredentialsRequest
from pydantic import ValidationError
from ollama import Client


def mcp_call(method, params):
    """Helper function to make JSON-RPC calls to the MCP server"""
    url = settings.MCP_ENDPOINT if hasattr(settings, 'MCP_ENDPOINT') else "http://localhost:8000/mcp"

    # Prepare JSON-RPC 2.0 request
    rpc_request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1  # Simple ID for request tracking
    }

    # Make the request
    response = requests.post(url, json=rpc_request)
    response.raise_for_status()
    return response.json()


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
    Open a new account in the database using either direct REST API or MCP.
    Uses environment variable to determine which method to call.
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

    # Determine which method to use based on environment
    use_mcp = getattr(settings, 'USE_MCP', 'false').lower() == 'true'

    if use_mcp:
        # Use MCP JSON-RPC approach
        try:
            rpc_request = {
                "jsonrpc": "2.0",
                "method": "insert_credentials",
                "params": payload,
                "id": 1
            }
            print(f"📤 MCP request: {rpc_request}")

            rpc_resp = mcp_call('insert_credentials', payload)  # Note: method name from mcp.yaml
            print(f"📥 MCP response: {rpc_resp}")

            if 'result' in rpc_resp:
                new_id = rpc_resp['result'].get('inserted_id')
                print(f"✅ New account created with id: {new_id}")
            else:
                error = rpc_resp.get('error', {})
                print(f"❌ MCP error: {error}")
        except requests.RequestException as err:
            print(f"❌ HTTP error calling MCP server: {err}")
    else:
        # Use direct REST API approach
        url = settings.REST_ENDPOINT if hasattr(settings, 'REST_ENDPOINT') else "http://localhost:8000/insert_user"
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            new_id = data.get("inserted_id")
            print(f"✅ New account created with id: {new_id}")
        except requests.RequestException as err:
            print(f"❌ Failed to create account: {err}")