# agents/actions/pathao_data_add.py

import json
import requests
from ollama import Client, ResponseError
from agents.config import settings


import string
from typing import Callable, Dict, Optional


import string
from typing import Callable, Dict, Optional


import string
from typing import Callable, Dict, Optional

import string
from typing import Callable, Dict, Optional

import json
from ollama import Client
from agents.config import settings
from agents.payload_generators.pathao_ride_request import PathaoConfig, PathaoPayloadGenerator
from agents.payload_generators.pathao_ride_started import PathaoRideStartedGenerator
from agents.payload_generators.pathao_ride_finished import PathaoTripFinishedGenerator
import time




def handle_full_trip_data(client: Client, project: str, auth_token: str):
    print(f"\n📊 Collecting FULL TRIP DATA for '{project}'")
    payload = {
        "trip_id":   input("• Trip ID: ").strip(),
        "pickup":    input("• Pickup location: ").strip(),
        "dropoff":   input("• Dropoff location: ").strip(),
        "distance":  input("• Distance (km): ").strip(),
        "duration":  input("• Duration (minutes): ").strip(),
        "fare":      input("• Fare amount: ").strip(),
        "timestamp": input("• Timestamp (YYYY-MM-DD HH:MM:SS): ").strip(),
    }

    url = getattr(settings, "PATHAO_FULL_TRIP_ENDPOINT",
                  "https://gigly-recommendation-engine-service-api.global.fintech23.xyz/api/v1/pathao/full-trip-data")
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept":        "application/json",
        "Content-Type":  "application/json",
    }

    print(f"\n🚀 POST {url}\nHeaders: {headers}\nPayload:\n{json.dumps(payload, indent=2)}\n")
    resp = requests.post(url, headers=headers, json=payload)
    try:
        resp.raise_for_status()
        print("✅ Success:", resp.json())
    except requests.HTTPError as e:
        print("❌ Error:", e, resp.text)


def generate_ride_request_payload_via_llm(client: Client) -> dict:
    """
    Ask the LLM to generate a Pathao ride-request payload.
    Uses your real example as a system prompt and returns the JSON dict.
    """
    system_prompt = (
        "You are a JSON payload generator for Pathao ride requests.\n"
        "Generate a JSON object with exactly these keys:\n"
        "  id (integer), fare (string), bonus (string), pickup_location (string),\n"
        "  destination_location (string), distance (string), is_surge (boolean),\n"
        "  coordinates (string), device_id (string), timestamp (integer).\n"
        "Do not wrap in markdown or extra commentary—output only the JSON."
    )
    try:
        resp = client.chat(
            model="deepseek-r1:8b",
            messages=[
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": ""}
            ]
        )
        content = resp.message.content.strip()
        # strip markdown fences if present
        import re
        m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        json_str = m.group(1) if m else content
        return json.loads(json_str)
    except (ResponseError, json.JSONDecodeError) as e:
        print(f"❌ Failed to generate via AI: {e}")
        return {}



def handle_ride_request_data(client: Client, project: str, auth_token: str):
    """
    Collects a Pathao ride-request payload—either auto-generated via LLM
    or fallback/random—and POSTs it with the Bearer token.
    """
    print(f"\n📥 Collecting RIDE REQUEST for '{project}'\n")

    # 1) Initialize your payload generator
    cfg = PathaoConfig(
        auth_token=auth_token,
        device_id=settings.DEVICE_ID  # or wherever you store it
    )
    gen = PathaoPayloadGenerator(cfg, client)

    # 2) Ask whether to auto-generate via AI
    # choice = input("Auto-generate ride-request payload via AI? (y/n) [y]: ")\
    #          .strip().lower() or "y"
    choice = 'y'  # Default to 'yes' for easier testing
    if choice in ("y", "yes"):
        print("🤖 Generating ride-request payload via AI...\n")
        # Let the LLM generate it (with fallback if the model fails)
        payload = gen.generate_via_llm()
        print(f"\n✅ AI-generated payload:\n{json.dumps(payload, indent=2)}\n")
    else:
        # Use the built-in fallback generator directly
        print("⚠️ Manual entry skipped—using random fallback payload.\n")
        payload = gen._fallback_payload()
        print(f"\n🎲 Fallback payload:\n{json.dumps(payload, indent=2)}\n")

    # 3) Send the request
    success = gen.send_request(payload)
    if not success:
        print("❌ Failed to send ride-request payload.")


def handle_ride_started_data(
    client: Client,
    project: str,
    auth_token: str,
    use_ai_default: bool = True,
):
    """
    Collects a Pathao 'ride_started' payload—either auto-generated via LLM,
    manual-entry fallback, or random fallback—and POSTs it.
    """
    print(f"\n▶️ Collecting RIDE STARTED for '{project}'\n")

    # 1) Prepare generator
    cfg = PathaoConfig(
        auth_token=auth_token,
        device_id=settings.DEVICE_ID,
        base_url=getattr(
            settings,
            "PATHAO_RIDE_STARTED_ENDPOINT",
            "https://gigly-recommendation-engine-service-api.global.fintech23.xyz"
            "/api/v1/pathao/raw-ride-started"
        )
    )
    gen = PathaoRideStartedGenerator(cfg, client)

    # 2) Ask whether to auto-generate via AI
    prompt = "Auto-generate ride_started payload via AI? (y/n)"
    # choice = input(f"{prompt} [{'Y' if use_ai_default else 'n'}]: ").strip().lower()
    choice = "y"
    if not choice:
        choice = 'y' if use_ai_default else 'n'

    if choice in ("y", "yes"):
        print("🤖 Generating ride_started payload via AI...\n")
        payload = gen.generate_via_llm()

    else:
        # 3) Manual entry fallback
        print("✍️  Please enter ride_started details:")
        payload = {
            "ride_id":           input("• Ride ID: ").strip(),
            "driver_id":         input("• Driver ID: ").strip(),
            "start_time":        input("• Start time (YYYY-MM-DD HH:MM:SS): ").strip(),
            "event":             "ride_started",
            "device_id":         settings.DEVICE_ID,
            "timestamp":         int(time.time() * 1000),
        }

    print(f"\n✅ Payload ready:\n{json.dumps(payload, indent=2)}\n")

    # 4) Send it
    success = gen.send_request(payload)
    if not success:
        print("❌ Failed to send ride_started payload.")


def handle_ride_finished_data(
    client: Client,
    project: str,
    auth_token: str,
    use_ai_default: bool = True
):
    """
    Collects a Pathao 'trip_finished' payload—either auto-generated via LLM
    or manual—and POSTs it with the Bearer token.
    """
    print(f"\n⏹️ Collecting TRIP FINISHED for '{project}'\n")

    # 1) Prepare the generator
    cfg = PathaoConfig(
        auth_token=auth_token,
        device_id=settings.DEVICE_ID,
        base_url=getattr(
            settings,
            "PATHAO_TRIP_FINISHED_ENDPOINT",
            "https://gigly-recommendation-engine-service-api.global.fintech23.xyz"
            "/api/v1/pathao/raw-trip-finished"
        )
    )
    gen = PathaoTripFinishedGenerator(cfg, client)

    # 2) Ask whether to auto-generate via AI
    default = 'Y' if use_ai_default else 'n'
    # choice = input(f"Auto-generate trip_finished payload via AI? (y/n) [{default}]: ")\
             # .strip().lower()
    choice = 'y'  # Default to 'yes' for easier testing
    if not choice:
        choice = 'y' if use_ai_default else 'n'

    if choice in ("y", "yes"):
        print("🤖 Generating trip_finished payload via AI...\n")
        payload = gen.generate_via_llm()
    else:
        # 3) Manual-entry fallback
        print("✍️  Please enter trip_finished details:\n")
        coords   = input("• Coordinates (e.g. \"[23.78, 90.39]\"): ").strip()
        discount = input("• Discount message: ").strip()
        fare     = input("• Fare (e.g. \"58.10\"): ").strip()

        payload = {
            "coordinates": coords,
            "device_id":   settings.DEVICE_ID,
            "discount":    discount,
            "fare":        fare,
            "timestamp":   int(time.time() * 1000),
        }

    # 4) Show & send
    print(f"\n✅ Payload:\n{json.dumps(payload, indent=2)}\n")
    success = gen.send_request(payload)
    if not success:
        print("❌ Failed to send trip_finished payload.")


def handle_trip_receipt_data(client: Client, project: str, auth_token: str):
    print(f"\n🧾 Collecting TRIP RECEIPT for '{project}'")
    payload = {
        "receipt_id":   input("• Receipt ID: ").strip(),
        "trip_id":      input("• Trip ID: ").strip(),
        "items":        input("• Receipt items (comma-separated): ").split(","),
        "total_amount": input("• Total amount: ").strip(),
    }

    url = getattr(settings, "PATHAO_TRIP_RECEIPT_ENDPOINT",
                  "https://gigly-recommendation-engine-service-api.global.fintech23.xyz/api/v1/pathao/raw-trip-receipt")
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept":        "application/json",
        "Content-Type":  "application/json",
    }

    print(f"\n🚀 POST {url}\nHeaders: {headers}\nPayload:\n{json.dumps(payload, indent=2)}\n")
    resp = requests.post(url, headers=headers, json=payload)
    try:
        resp.raise_for_status()
        print("✅ Success:", resp.json())
    except requests.HTTPError as e:
        print("❌ Error:", e, resp.text)
