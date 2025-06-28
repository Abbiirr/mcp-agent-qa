import requests
from config import settings
from schemas.schemas import InsertCredentialsRequest
from pydantic import ValidationError
from ollama import Client
import json


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


def generate_payload_via_llm(client: Client) -> dict:
    """
    Ask the LLM to build a JSON payload for InsertCredentialsRequest.
    With guaranteed unique user_id, email, and phone_number.
    """
    system_prompt = (
        "You are a JSON payload generator. "
        "Produce a JSON object with exactly these keys: "
        "user_id (string), first_name (string), last_name (string), "
        "email (string or null), phone_number (string or null), is_active (boolean). "
        "Do not wrap it in any markdown or extra text—only output the JSON."
    )
    # empty user content: we just want the structure
    response = client.chat(
        model="deepseek-r1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ""}
        ]
    )

    # Get the raw content from the response dictionary
    content = response['message']['content']
    print(f"Raw LLM response: {content}")

    # Extract JSON if it's wrapped in markdown code blocks
    import re
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
    if json_match:
        content = json_match.group(1)

    # Try to parse the JSON
    try:
        import uuid
        import random
        from datetime import datetime

        # Parse initial payload from LLM
        payload = json.loads(content)

        # Generate unique values
        timestamp = datetime.now().strftime("%m%d%H%M")
        unique_id = uuid.uuid4().hex[:8]

        # Keep the LLM-generated names but ensure unique identifiers
        first_name = payload.get("first_name", "User")
        last_name = payload.get("last_name", "Test")

        # Override with unique values
        payload["user_id"] = f"{first_name.lower()}_{timestamp}_{unique_id}"
        payload["email"] = f"{first_name.lower()}.{last_name.lower()}.{unique_id}@example.com"
        # Replace the phone_number line with this:
        payload[
            "phone_number"] = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

        print(f"✅ Generated payload with unique values: {json.dumps(payload, indent=2)}")
        return payload
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON from LLM: {e}")
        print(f"Content that failed to parse: {content}")
        return {}

def handle_open_new_account(client: Client, project: str):
    print(f"\n🚀 Opening a new account for project '{project}'\n")

    # 1) Ask if AI should fill the payload
    choice = input("Generate account details automatically via AI? (y/n) [y]: ").strip().lower() or "y"
    if choice in ("y", "yes"):
        payload = generate_payload_via_llm(client)
        if not payload:
            print("❌ Aborting: payload generation failed.")
            return
    else:
        # Manual entry
        payload = {
            "user_id":      input("• Enter user_id: ").strip(),
            "first_name":   input("• Enter first name: ").strip(),
            "last_name":    input("• Enter last name: ").strip(),
            "email":        input("• Enter email (optional): ").strip() or None,
            "phone_number": input("• Enter phone number (optional): ").strip() or None,
            "is_active":    (input("• Is the account active? (y/n) [y]: ").strip() or "y").lower() not in ("n","no")
        }

    # 2) Validate payload
    try:
        InsertCredentialsRequest(**payload)
    except ValidationError as ve:
        print("\n❌ Validation error:")
        print(ve)
        return

    # 3) Call via MCP or REST
    use_mcp = getattr(settings, 'USE_MCP', 'false').lower() == 'true'
    if use_mcp:
        print("\n📤 Sending JSON-RPC to MCP server…")
        try:
            rpc_resp = mcp_call("insert_credentials", payload)
            print("📥 MCP response:", json.dumps(rpc_resp, indent=2))
            if "result" in rpc_resp:
                # For MCP path (replace the current line):
                print(
                    f"\n✅ New account created: user_id={payload['user_id']}, email={payload.get('email')}, phone={payload.get('phone_number')}")
            else:
                print("❌ MCP error:", rpc_resp.get("error"))
        except (requests.RequestException, ValidationError) as err:
            print("❌ MCP call failed:", err)
    else:
        rest_url = getattr(settings, 'REST_ENDPOINT', "http://localhost:8000/insert_user")
        print(f"\n📤 Sending direct POST to {rest_url} …")
        try:
            resp = requests.post(rest_url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # For REST API path (replace the current line):
            print(
                f"\n✅ New account created: user_id={payload['user_id']}, email={payload.get('email')}, phone={payload.get('phone_number')}")
        except requests.RequestException as err:
            print("❌ REST call failed:", err)
        except ValueError:
            print("❌ Invalid JSON response:", resp.text)