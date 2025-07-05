# agents/actions/pathao_data_add.py
import json
import requests
import time
from typing import Dict, Optional
from ollama import Client, ResponseError
from agents.config import settings

from agents.payload_generators.pathao_ride_request import PathaoConfig, PathaoPayloadGenerator
from agents.payload_generators.pathao_ride_started import PathaoRideStartedGenerator
from agents.payload_generators.pathao_ride_finished import PathaoTripFinishedGenerator

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


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

    url = getattr(
        settings, "PATHAO_FULL_TRIP_ENDPOINT",
        "https://gigly-recommendation-engine-service-api.global.fintech23.xyz/api/v1/pathao/full-trip-data"
    )
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept":        "application/json",
        "Content-Type":  "application/json",
    }

    print(f"\n🚀 POST {url}\nHeaders: {headers}\nPayload:\n{json.dumps(payload, indent=2)}\n")
    success = False
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            print("✅ Success:", resp.json())
            success = True
            break
        except requests.HTTPError as e:
            print(f"❌ HTTP {resp.status_code} – {resp.text}")
        except Exception as e:
            print(f"❌ Request error: {e}")
        if attempt < MAX_RETRIES:
            print(f"⏳ Retrying ({attempt}/{MAX_RETRIES}) in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    if not success:
        print(f"❌ Failed to send full trip data after {MAX_RETRIES} attempts.")


def handle_ride_request_data(client: Client, project: str, auth_token: str):
    print(f"\n📥 Collecting RIDE REQUEST for '{project}'\n")
    cfg = PathaoConfig(auth_token=auth_token, device_id=settings.DEVICE_ID)
    gen = PathaoPayloadGenerator(cfg, client)

    payload = gen.generate_via_llm()
    print(f"\n✅ Payload ready:\n{json.dumps(payload, indent=2)}\n")

    success = False
    for attempt in range(1, MAX_RETRIES + 1):
        if gen.send_request(payload):
            success = True
            break
        print(f"❌ Attempt {attempt} failed, retrying in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
    if not success:
        print(f"❌ Failed to send ride_request payload after {MAX_RETRIES} attempts.")


def handle_ride_started_data(
    client: Client,
    project: str,
    auth_token: str,
    use_ai_default: bool = True,
):
    print(f"\n▶️ Collecting RIDE STARTED for '{project}'\n")
    cfg = PathaoConfig(
        auth_token=auth_token,
        device_id=settings.DEVICE_ID,
        base_url=getattr(
            settings,
            "PATHAO_RIDE_STARTED_ENDPOINT",
            "https://gigly-recommendation-engine-service-api.global.fintech23.xyz/api/v1/pathao/raw-ride-started"
        )
    )
    gen = PathaoRideStartedGenerator(cfg, client)
    payload = gen.generate_via_llm()
    print(f"\n✅ Payload ready:\n{json.dumps(payload, indent=2)}\n")

    success = False
    for attempt in range(1, MAX_RETRIES + 1):
        if gen.send_request(payload):
            success = True
            break
        print(f"❌ Attempt {attempt} failed, retrying in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
    if not success:
        print(f"❌ Failed to send ride_started payload after {MAX_RETRIES} attempts.")


def handle_ride_finished_data(
    client: Client,
    project: str,
    auth_token: str,
    use_ai_default: bool = True
):
    print(f"\n⏹️ Collecting TRIP FINISHED for '{project}'\n")
    cfg = PathaoConfig(
        auth_token=auth_token,
        device_id=settings.DEVICE_ID,
        base_url=getattr(
            settings,
            "PATHAO_TRIP_FINISHED_ENDPOINT",
            "https://gigly-recommendation-engine-service-api.global.fintech23.xyz/api/v1/pathao/raw-trip-finished"
        )
    )
    gen = PathaoTripFinishedGenerator(cfg, client)
    payload = gen.generate_via_llm()
    print(f"\n✅ Payload ready:\n{json.dumps(payload, indent=2)}\n")

    success = False
    for attempt in range(1, MAX_RETRIES + 1):
        if gen.send_request(payload):
            success = True
            break
        print(f"❌ Attempt {attempt} failed, retrying in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
    if not success:
        print(f"❌ Failed to send ride_finished payload after {MAX_RETRIES} attempts.")


def handle_trip_receipt_data(client: Client, project: str, auth_token: str):
    print(f"\n🧾 Collecting TRIP RECEIPT for '{project}'")
    payload = {
        "receipt_id":   input("• Receipt ID: ").strip(),
        "trip_id":      input("• Trip ID: ").strip(),
        "items":        input("• Receipt items (comma-separated): ").split(","),
        "total_amount": input("• Total amount: ").strip(),
    }

    url = getattr(
        settings,
        "PATHAO_TRIP_RECEIPT_ENDPOINT",
        "https://gigly-recommendation-engine-service-api.global.fintech23.xyz/api/v1/pathao/raw-trip-receipt"
    )
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept":        "application/json",
        "Content-Type":  "application/json",
    }
    print(f"\n🚀 POST {url}\nHeaders: {headers}\nPayload:\n{json.dumps(payload, indent=2)}\n")

    success = False
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            print("✅ Success:", resp.json())
            success = True
            break
        except requests.HTTPError as e:
            print(f"❌ HTTP {resp.status_code} – {resp.text}")
        except Exception as e:
            print(f"❌ Request error: {e}")
        print(f"❌ Attempt {attempt} failed, retrying in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
    if not success:
        print(f"❌ Failed to send trip_receipt payload after {MAX_RETRIES} attempts.")


def handle_summaries_action(
    client: Client,
    project: str,
    auth_token: str,
    range: str = "ONE_WEEK",
    language: str = "EN"
) -> Optional[Dict]:
    print(f"\n📈 Fetching TOTAL TRIPS SUMMARY for '{project}' (range={range})\n")
    url = getattr(
        settings,
        "USER_SERVICE_SUMMARY_ENDPOINT",
        "https://giglytech-user-service-api.global.fintech23.xyz/api/v1/user/summary/total-trips"
    )
    headers = {
        "accept":           "application/json",
        "Accept-Language":  language,
        "Authorization":    f"Bearer {auth_token}",
    }
    params = {"range": range}
    print(f"🚀 GET {url}?range={range}\nHeaders: {headers}\n")

    attempt = 0
    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            summary = resp.json()
            print("✅ Summary Data:\n", json.dumps(summary, indent=2))
            return summary
        except requests.HTTPError as e:
            print(f"❌ HTTP {resp.status_code} – {resp.text}")
        except Exception as e:
            print(f"❌ Request error: {e}")
        if attempt < MAX_RETRIES:
            print(f"⏳ Retrying summary fetch ({attempt}/{MAX_RETRIES}) in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    print(f"❌ Failed to fetch summary after {MAX_RETRIES} attempts.")
    return None
