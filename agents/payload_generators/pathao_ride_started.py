import json
import random
import time
import re
import requests
from typing import Dict
from ollama import Client, ResponseError
from agents.config import settings

class PathaoRideStartedGenerator:
    """LLM-backed and fallback payload generator for Pathao ride_started events."""

    def __init__(self, config: settings, client: Client):
        self.config = config
        self.client = client
        # sample locations and coordinates for fallback
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
            "You are a JSON payload generator for Pathao ride_started events in Dhaka.\n"
            "Use this example as your template—output must match it exactly (keys, types, and ordering):\n"
            "{\n"
            "  \"coordinates\": \"[23.7816814, 90.399625]\",\n"
            "  \"destination_location\": \"Banani, Dhaka\",\n"
            "  \"device_id\": \"57e2938aaa20c833\",\n"
            "  \"event\": \"ride_started\",\n"
            "  \"timestamp\": 1751440833703\n"
            "}\n"
            f"Always use device_id: \"{self.config.device_id}\" and event: \"ride_started\" with fresh timestamp.\n"
            "Output ONLY the JSON object—no markdown or extra text."
        )

    def _extract_json(self, text: str) -> str:
        # Try fenced JSON first
        m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if m:
            return m.group(1).strip()
        # Fallback to first {...}
        m2 = re.search(r'\{[\s\S]*\}', text)
        return m2.group(0).strip() if m2 else text.strip()

    def generate_via_llm(self) -> Dict:
        """Ask the LLM for a ride_started payload; fallback on error."""
        try:
            resp = self.client.chat(
                model="deepseek-r1:8b",
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user",   "content": "Please generate one ride_started payload."}
                ]
            )
            content = resp.message.content
            json_str = self._extract_json(content)
            payload = json.loads(json_str)
            # enforce our dynamic fields
            payload["device_id"] = self.config.device_id
            payload["event"] = "ride_started"
            payload["timestamp"] = int(time.time() * 1000)
            return payload
        except (ResponseError, json.JSONDecodeError, KeyError) as e:
            print(f"❌ LLM failed, using fallback: {e}")
            return self._fallback_payload()

    def _fallback_payload(self) -> Dict:
        """Generate a random-but-realistic ride_started payload."""
        dest = random.choice(self.locations)
        coord = random.choice(self.coords)
        return {
            "coordinates": coord,
            "destination_location": dest,
            "device_id": self.config.device_id,
            "event": "ride_started",
            "timestamp": int(time.time() * 1000)
        }

    def send_request(self, payload: Dict) -> bool:
        """POST the ride_started payload with the stored auth_token."""
        headers = {
            "Authorization": f"Bearer {self.config.auth_token}",
            "Accept":        "application/json",
            "Content-Type":  "application/json",
        }
        print(f"🚀 Sending POST {self.config.base_url}\nPayload:\n{json.dumps(payload, indent=2)}")
        try:
            r = requests.post(
                self.config.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            r.raise_for_status()
            print("✅ Success:", r.json())
            return True
        except requests.HTTPError:
            print(f"❌ HTTP {r.status_code} – {r.text}")
        except Exception as err:
            print(f"❌ Request error: {err}")
        return False
