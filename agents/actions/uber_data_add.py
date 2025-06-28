# agents/actions/uber_data_add.py
from ollama import Client

def handle_uber_data(client: Client, project: str):
    """
    Stub for collecting and saving Uber-specific data.
    """
    print(f"\n🚗 Uber data ingestion for project '{project}'")
    # Example questions — you can extend these as needed:
    ride_id   = input("• Enter Uber ride ID: ").strip()
    origin    = input("• Enter origin location: ").strip()
    destination = input("• Enter destination location: ").strip()
    cost      = input("• Enter ride cost: ").strip()
    time      = input("• Enter ride timestamp (YYYY-MM-DD HH:MM:SS): ").strip()

    # TODO: validate & package into your schema, then either:
    #   • call mcp_call("insert_uber_ride", {...})
    #   • or do a direct REST POST to /insert_uber_ride
    print(f"\n✅ Collected Uber ride: {ride_id}, from {origin} to {destination} at {time}, cost {cost}\n")