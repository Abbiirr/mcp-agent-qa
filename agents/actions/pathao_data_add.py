# agents/actions/pathao_data_add.py

import json
import requests
from ollama import Client
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
from config import settings
from agents.payload_generators.pathao_ride_request import PathaoConfig, PathaoPayloadGenerator




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
    choice = input("Auto-generate ride-request payload via AI? (y/n) [y]: ")\
             .strip().lower() or "y"

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


def handle_ride_started_data(client: Client, project: str, auth_token: str):
    print(f"\n▶️ Collecting RIDE STARTED for '{project}'")
    payload = {
        "ride_id":    input("• Ride ID: ").strip(),
        "driver_id":  input("• Driver ID: ").strip(),
        "start_time": input("• Start time (YYYY-MM-DD HH:MM:SS): ").strip(),
    }

    url = getattr(settings, "PATHAO_RIDE_STARTED_ENDPOINT",
                  "https://gigly-recommendation-engine-service-api.global.fintech23.xyz/api/v1/pathao/raw-ride-started")
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


def handle_ride_finished_data(client: Client, project: str, auth_token: str):
    print(f"\n⏹️ Collecting RIDE FINISHED for '{project}'")
    payload = {
        "ride_id":     input("• Ride ID: ").strip(),
        "end_time":    input("• End time (YYYY-MM-DD HH:MM:SS): ").strip(),
        "total_fare":  input("• Total fare: ").strip(),
        "cancelled":   input("• Cancelled? (y/n) [n]: ").strip().lower() in ("y", "yes"),
    }

    url = getattr(settings, "PATHAO_RIDE_FINISHED_ENDPOINT",
                  "https://gigly-recommendation-engine-service-api.global.fintech23.xyz/api/v1/pathao/raw-ride-finished")
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
