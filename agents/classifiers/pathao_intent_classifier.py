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

from agents.actions.pathao_data_add import (
handle_full_trip_data,
handle_ride_request_data,
handle_ride_started_data,
handle_ride_finished_data,
handle_trip_receipt_data
)

def handle_pathao_data(
        client: Client,
        project: str,
        auth_token: str,
        max_retries: int = 3
) -> None:
    """
    Uses *only* LLM intent classification to dispatch to the right Pathao data handler.
    Retries up to `max_retries` times if the category isn't recognized.
    """
    print(f"\n🚴 Pathao data ingestion for project '{project}'\n")

    # 1) Define categories & handlers
    categories = [
        "full trip data",
        "ride request",
        "ride started",
        "ride finished",
        "trip receipt",
    ]
    handlers: Dict[str, Callable[[Client, str, str], None]] = {
        "full trip data": handle_full_trip_data,
        "ride request": handle_ride_request_data,
        "ride started": handle_ride_started_data,
        "ride finished": handle_ride_finished_data,
        "trip receipt": handle_trip_receipt_data,
    }

    # 2) Helper to extract answer from reasoning models
    def extract_answer(text: str) -> str:
        import re

        # First, try to extract content after </think> tag (for reasoning models)
        think_match = re.search(r'</think>\s*(.*?)$', text, re.DOTALL | re.IGNORECASE)
        if think_match:
            extracted = think_match.group(1).strip()
            print(f"[DEBUG] Extracted after </think>: '{extracted}'")
            return extracted

        # If no think tags, return the original text
        return text.strip()

    # 3) Normalization helper
    def normalize(text: str) -> str:
        txt = text.lower().strip()
        # Remove quotes and extra punctuation, but keep spaces
        txt = txt.strip('"\'.,!?')
        return "".join(ch for ch in txt if ch.isalnum() or ch.isspace()).strip()

    # 4) Build the system prompt once
    system_prompt = (
            "You are an intent classifier for Pathao ride-sharing data.\n"
            "Classify the user's request into exactly one of the following categories:\n"
            + "\n".join(f"- {cat}" for cat in categories)
            + "\n\nReply with *only* the exact category name from the list above, no other words or explanations."
    )

    # 5) Retry loop
    for attempt in range(1, max_retries + 1):
        print("❓ What Pathao data would you like to add?")
        print("(e.g., \"I need the trip receipt\" or just paste your free-form request)\n")

        user_input = input("Your request: ").strip()
        print(f"[DEBUG] User input: {user_input}")

        print("🤖 Classifying with LLM...")
        try:
            resp = client.chat(
                model="deepseek-r1:8b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
            )
            llm_reply = resp["message"]["content"]
        except Exception as e:
            print(f"❌ LLM call failed: {e}")
            return

        print(f"[DEBUG] Raw LLM reply: '{llm_reply}'")

        # Extract the actual answer (handles reasoning models)
        extracted_answer = extract_answer(llm_reply)
        print(f"[DEBUG] Extracted answer: '{extracted_answer}'")

        # Normalize for comparison
        norm_reply = normalize(extracted_answer)
        print(f"[DEBUG] Normalized answer: '{norm_reply}'")

        # 6) Match against our normalized categories
        raw_to_norm = {normalize(cat): cat for cat in categories}
        print(f"[DEBUG] Normalized categories: {list(raw_to_norm.keys())}")

        selected = raw_to_norm.get(norm_reply)

        if selected:
            print(f"✅ Classified as: {selected}\n")
            handlers[selected](client, project, auth_token)
            return
        else:
            # Try partial matching as fallback
            print(f"[DEBUG] Exact match failed, trying partial matching...")
            best_match = None
            best_score = 0

            for cat in categories:
                cat_words = normalize(cat).split()
                reply_words = norm_reply.split()

                # Count matching words
                matches = sum(1 for word in cat_words if word in reply_words)
                score = matches / len(cat_words) if cat_words else 0

                print(f"[DEBUG] '{cat}' matches: {matches}/{len(cat_words)} = {score:.2f}")

                if score > best_score:
                    best_score = score
                    best_match = cat

            if best_score >= 0.5:  # At least 50% word match
                print(f"✅ Partial match found: {best_match} (score: {best_score:.2f})\n")
                handlers[best_match](client, project, auth_token)
                return

            print(f"⚠️  \"{extracted_answer}\" is not one of the valid categories.")
            if attempt < max_retries:
                print(f"🔁 Retrying classification ({attempt + 1}/{max_retries})...\n")
            else:
                print("\n❌ Giving up after multiple attempts. Please try again later.\n")
                return

