import time
from typing import Optional
from ollama import Client
from agents.config import settings
from agents.actions.summary_actions import handle_total_trips_summary
from agents.actions.pathao_data_add import (
    handle_ride_request_data,
    handle_ride_started_data,
    handle_ride_finished_data
)

def verify_trip_increment(
    client: Client,
    project: str,
    auth_token: str,
    range: str = "ONE_WEEK",
    language: str = "EN"
) -> Optional[bool]:
    """
    1) Fetches the initial totalTrips summary.
    2) Sends a ride-request, ride-started, and trip-finished event.
    3) Fetches the new summary and verifies totalTrips incremented by 1.

    Returns True if increment is correct, False otherwise, or None on error.
    """
    # 1) Initial summary
    summary_before = handle_total_trips_summary(client, project, auth_token, range, language)
    if not summary_before or "data" not in summary_before:
        print("❌ Failed to fetch initial summary.")
        return None
    initial_total = summary_before["data"].get("totalTrips")
    if initial_total is None:
        print("❌ 'totalTrips' missing in initial summary.")
        return None
    print(f"Initial totalTrips = {initial_total}")

    # 2) Send the three events
    print("\n🔄 Sending a full trip (request → started → finished) sequence...\n")
    handle_ride_request_data(client, project, auth_token)
    time.sleep(0.2)
    handle_ride_started_data(client, project, auth_token)
    time.sleep(0.2)
    handle_ride_finished_data(client, project, auth_token)
    print("✅ Full trip sequence sent successfully.")
    print("⏳ Waiting for the summary to update...")
    print("Please wait at least 1 minute before checking the new summary.\n")
    time.sleep(1.1*60)

    # 3) New summary
    summary_after = handle_total_trips_summary(client, project, auth_token, range, language)
    if not summary_after or "data" not in summary_after:
        print("❌ Failed to fetch new summary.")
        return None
    new_total = summary_after["data"].get("totalTrips")
    if new_total is None:
        print("❌ 'totalTrips' missing in new summary.")
        return None
    print(f"New totalTrips = {new_total}")

    # 4) Verify increment
    expected = initial_total + 1
    if new_total == expected:
        print("✅ totalTrips incremented by 1 as expected.")
        return True
    else:
        print(f"❌ totalTrips did not increment as expected: expected {expected}, got {new_total}")
        return False
