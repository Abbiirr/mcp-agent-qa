import json
import re
import time
import random
import requests
from typing import Dict, List
from dataclasses import dataclass
from ollama import Client, ResponseError
from agents.config import settings

@dataclass
class PathaoConfig:
    """Configuration for Pathao ride request generation"""
    auth_token: str
    device_id: str
    # Use your real REST URL here
    base_url: str = (
        "https://gigly-recommendation-engine-service-api.global.fintech23.xyz"
        "/api/v1/pathao/raw-ride-request"
    )

class PathaoPayloadGenerator:
    """LLM-backed and fallback payload generator for Pathao ride requests."""

    def __init__(self, config: PathaoConfig, client: Client):
        self.config = config
        self.client = client
        self.locations = [
            "Continental Insurance Limited, Head Office, Amtoli, Mohakhali",
            "Dhanmondi 27, Dhaka",
            "Gulshan 2, Dhaka",
            "Banani, Dhaka",
            "Uttara Sector 3, Dhaka",
        ]
        self.coords = [
            "[23.7817088, 90.399587]",
            "[23.7461, 90.3742]",
            "[23.7925, 90.4077]",
            "[23.7936, 90.4066]",
            "[23.8759, 90.3795]",
        ]

    def _system_prompt(self) -> str:
        return (
            "You are a JSON payload generator for Pathao ride requests in Dhaka.\n"
            "Keys: id (int), fare (string, e.g. \"৳142.82\"), bonus (string),\n"
            "pickup_location (string), destination_location (string), distance (string, \"X.XX KM\"),\n"
            "is_surge (boolean), coordinates (string), device_id (string), timestamp (int).\n"
            f"Use device_id: \"{self.config.device_id}\".\n"
            "Output ONLY the JSON object—no markdown or extra text."
        )

    def _extract_json(self, text: str) -> str:
        m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if m: return m.group(1).strip()
        m2 = re.search(r'\{[\s\S]*\}', text)
        return m2.group(0).strip() if m2 else text.strip()

    def generate_via_llm(self) -> Dict:
        """Ask the LLM for a payload; fallback to random if parsing fails."""
        try:
            resp = self.client.chat(
                model="deepseek-r1:8b",
                messages=[
                    {"role":"system","content":self._system_prompt()},
                    {"role":"user","content":"Please generate one payload."}
                ]
            )
            content = resp.message.content
            json_str = self._extract_json(content)
            payload = json.loads(json_str)
            # override dynamic fields
            payload["device_id"] = self.config.device_id
            payload["timestamp"] = int(time.time() * 1000)
            return payload
        except (ResponseError, json.JSONDecodeError, KeyError) as e:
            print(f"❌ LLM failed, using fallback: {e}")
            return self._fallback_payload()

    def _fallback_payload(self) -> Dict:
        """Generate a random-but-realistic payload."""
        pickup = random.choice(self.locations)
        dest = random.choice(self.locations)
        while dest == pickup:
            dest = random.choice(self.locations)
        return {
            "id": random.randint(10000, 99999),
            "fare": f"৳{random.randint(80,300)}.{random.randint(10,99)}",
            "bonus": f"৳{random.randint(5,25)}",
            "pickup_location": pickup,
            "destination_location": dest,
            "distance": f"{random.uniform(1.5,15):.2f} KM",
            "is_surge": random.choice([False, False, False, True]),
            "coordinates": random.choice(self.coords),
            "device_id": settings.DEVICE_ID,
            "timestamp": int(time.time() * 1000)
        }

    def send_request(self, payload: Dict) -> bool:
        """POST the payload with the stored auth_token."""
        headers = {
            "Authorization": f"Bearer {settings.AUTH_TOKEN}",
            "Accept":        "application/json",
            "Content-Type":  "application/json",
        }
        print(f"\n🚀 Sending POST {self.config.base_url}\nHeaders: {headers}\nPayload:\n{json.dumps(payload, indent=2)}")
        try:
            r = requests.post(self.config.base_url, headers=headers, json=payload, timeout=10)
            r.raise_for_status()
            print("✅ Success:", r.json())
            return True
        except requests.HTTPError as err:
            print(f"❌ HTTP {r.status_code} – {r.text}")
        except Exception as err:
            print(f"❌ Request error: {err}")
        return False