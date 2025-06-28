# agents/actions/pathao_data_add.py

from ollama import Client

def handle_pathao_data(client: Client, project: str):
    """
    Stub for collecting and saving Pathao-specific data.
    First asks which class of Pathao data to save, then routes to the right handler.
    """
    print(f"\n🚴 Pathao data ingestion for project '{project}'\n")

    classes = [
        "full trip data",
        "ride request",
        "ride started",
        "ride finished",
        "trip receipt",
    ]

    # Show the menu
    print("Which Pathao data would you like to add?")
    for idx, name in enumerate(classes, start=1):
        print(f"  {idx}. {name.title()}")
    choice = input("Select by number or exact name: ").strip().lower()

    # Normalize selection
    if choice.isdigit() and 1 <= int(choice) <= len(classes):
        cls = classes[int(choice) - 1]
    else:
        cls = next((c for c in classes if c == choice), None)

    # Dispatch
    if cls == "full trip data":
        handle_full_trip_data(client, project)
    elif cls == "ride request":
        handle_ride_request_data(client, project)
    elif cls == "ride started":
        handle_ride_started_data(client, project)
    elif cls == "ride finished":
        handle_ride_finished_data(client, project)
    elif cls == "trip receipt":
        handle_trip_receipt_data(client, project)
    else:
        print(f"\n❌ Invalid selection '{choice}'. Please try again.\n")

def handle_full_trip_data(client: Client, project: str):
    print(f"\n📊 Collecting FULL TRIP DATA for '{project}'")
    trip_id   = input("• Trip ID: ").strip()
    pickup    = input("• Pickup location: ").strip()
    dropoff   = input("• Dropoff location: ").strip()
    distance  = input("• Distance (km): ").strip()
    duration  = input("• Duration (minutes): ").strip()
    fare      = input("• Fare amount: ").strip()
    timestamp = input("• Timestamp (YYYY-MM-DD HH:MM:SS): ").strip()

    # TODO: validate & send via mcp_call("insert_full_trip", {...})
    print(f"\n✅ Collected full trip data:\n"
          f"  • trip_id={trip_id}\n"
          f"  • pickup={pickup}\n"
          f"  • dropoff={dropoff}\n"
          f"  • distance={distance} km\n"
          f"  • duration={duration} min\n"
          f"  • fare={fare}\n"
          f"  • timestamp={timestamp}\n")

def handle_ride_request_data(client: Client, project: str):
    print(f"\n📥 Collecting RIDE REQUEST for '{project}'")
    request_id = input("• Request ID: ").strip()
    user_id    = input("• User ID: ").strip()
    time       = input("• Request time (YYYY-MM-DD HH:MM:SS): ").strip()

    # TODO: validate & send via mcp_call("insert_ride_request", {...})
    print(f"\n✅ Collected ride request:\n"
          f"  • request_id={request_id}\n"
          f"  • user_id={user_id}\n"
          f"  • time={time}\n")

def handle_ride_started_data(client: Client, project: str):
    print(f"\n▶️ Collecting RIDE STARTED for '{project}'")
    ride_id    = input("• Ride ID: ").strip()
    driver_id  = input("• Driver ID: ").strip()
    start_time = input("• Start time (YYYY-MM-DD HH:MM:SS): ").strip()

    # TODO: validate & send via mcp_call("insert_ride_started", {...})
    print(f"\n✅ Collected ride started:\n"
          f"  • ride_id={ride_id}\n"
          f"  • driver_id={driver_id}\n"
          f"  • start_time={start_time}\n")

def handle_ride_finished_data(client: Client, project: str):
    print(f"\n⏹️ Collecting RIDE FINISHED for '{project}'")
    ride_id      = input("• Ride ID: ").strip()
    end_time     = input("• End time (YYYY-MM-DD HH:MM:SS): ").strip()
    total_fare   = input("• Total fare: ").strip()
    cancelled    = input("• Cancelled? (y/n) [n]: ").strip().lower() in ("y", "yes")

    # TODO: validate & send via mcp_call("insert_ride_finished", {...})
    print(f"\n✅ Collected ride finished:\n"
          f"  • ride_id={ride_id}\n"
          f"  • end_time={end_time}\n"
          f"  • total_fare={total_fare}\n"
          f"  • cancelled={cancelled}\n")

def handle_trip_receipt_data(client: Client, project: str):
    print(f"\n🧾 Collecting TRIP RECEIPT for '{project}'")
    receipt_id   = input("• Receipt ID: ").strip()
    trip_id      = input("• Trip ID: ").strip()
    items        = input("• Receipt items (comma-separated): ").strip()
    total_amount = input("• Total amount: ").strip()

    # TODO: validate & send via mcp_call("insert_trip_receipt", {...})
    print(f"\n✅ Collected trip receipt:\n"
          f"  • receipt_id={receipt_id}\n"
          f"  • trip_id={trip_id}\n"
          f"  • items=[{items}]\n"
          f"  • total_amount={total_amount}\n")
