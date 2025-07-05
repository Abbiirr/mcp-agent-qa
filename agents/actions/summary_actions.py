import json
import requests
from typing import Optional, Dict
from ollama import Client
from agents.config import settings


def handle_total_trips_summary(
    client: Client,
    project: str,
    auth_token: str,
    range: str = "ONE_WEEK",
    language: str = "EN"
) -> Optional[Dict]:
    """
    Fetches and returns a summary of total trips for the given project over a specified range.

    Args:
        client: Ollama Client, not used here but kept for consistency.
        project: Name of the project (for logging).
        auth_token: Bearer token for authorization.
        range: Time range to summarize (e.g., "ONE_DAY", "ONE_WEEK", "ONE_MONTH").
        language: Preferred language for the response (e.g., "EN", "BN").

    Returns:
        A dict containing the JSON summary on success, or None on failure.
    """
    print(f"\n📈 Fetching TOTAL TRIPS SUMMARY for '{project}' (range={range})\n")
    # Base endpoint; can be overridden in settings
    base_url = getattr(
        settings,
        "USER_SERVICE_SUMMARY_ENDPOINT",
        "https://giglytech-user-service-api.global.fintech23.xyz/api/v1/user/summary/total-trips"
    )
    headers = {
        "Accept":           "application/json",
        "Accept-Language":  language,
        "Authorization":    f"Bearer {auth_token}",
    }
    params = {"range": range}

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        summary = response.json()
        print("✅ Summary Data:\n", json.dumps(summary, indent=2))
        return summary
    except requests.HTTPError as http_err:
        print(f"❌ HTTP {response.status_code} – {response.text}")
    except Exception as err:
        print(f"❌ Request error: {err}")
    return None