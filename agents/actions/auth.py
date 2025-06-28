# agents/actions/auth.py

import requests
from agents.config import settings

def request_otp_and_get_session() -> str:
    """
    Phase 1: Sends a TFA/OTP request and returns the session ID.
    Only prompts the user for email or phone number; all other fields
    come directly from the example in request-tfa-1.txt.
    """
    url = getattr(
        settings,
        "TFA_REQUEST_OTP_ENDPOINT",
        "https://giglytech-user-service-api.global.fintech23.xyz"
        "/api/v1/user/tfa/request-otp"
    )
    headers = {
        "accept": "application/json",
        "Accept-Language": getattr(settings, "LANGUAGE", "EN"),
        "CurrentContext": getattr(settings, "CURRENT_CONTEXT", ""),
        "Content-Type": "application/json",
    }

    # Only ask for email or phone
    email_or_number = input("Enter email or phone number: ").strip()

    # Payload fields taken from your sample curl :contentReference[oaicite:5]{index=5}
    payload = {
        "emailOrNumber": email_or_number,
        "userType": "CUSTOMER",
        "deviceInfo": {
            "platformType":     "ANDROID",
            "platformInfo":     "Gp",
            "platformVersion":  "10.0.0",
            "deviceIdentifier": "74589653694541",
            "deviceId":         "74589653694541",
            "appLanguage":      "ENGLISH",
            "appVersion":       "1.0.0"
        },
        "tfaTypeCode": "1",
        "featureCode":  "40"
    }

    print(f"\n📤 Sending OTP request to {url} with payload:\n{payload}\n")
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()

    body = resp.json()
    session_id = body.get("data", {}).get("tokenSessionId")
    if not session_id:
        raise ValueError(f"No tokenSessionId in response: {body}")

    print(f"✅ tokenSessionId: {session_id}\n")
    return session_id

def verify_otp_and_get_token(token_session_id: str) -> str:
    """
    Phase 2: Verifies the OTP and returns the final auth token.
    """
    url = getattr(
        settings,
        "TFA_VERIFY_ENDPOINT",
        "https://giglytech-user-service-api.global.fintech23.xyz"
        "/api/v1/user/tfa/verification"
    )
    headers = {
        "accept": "application/json",
        "Accept-Language": getattr(settings, "LANGUAGE", "EN"),
        "CurrentContext": getattr(settings, "CURRENT_CONTEXT", ""),
        "Content-Type": "application/json",
    }
    otp           = input("Enter the OTP you received: ").strip()
    user_identity = input("Enter your userIdentity: ").strip()

    payload = {
        "sessionId":    token_session_id,
        "otp":          otp,
        "userIdentity": user_identity
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    body = resp.json()
    # Adjust key name if different (e.g., "token" or "accessToken")
    auth_token = body.get("data", {}).get("accessToken")
    if not auth_token:
        raise ValueError(f"No authToken in response: {body}")
    print(f"✅ authToken: {auth_token}\n")
    return auth_token

def login_and_get_token() -> str:
    """
    Combines the two phases: requests OTP, verifies it, and returns the auth token.
    """
    session_id = request_otp_and_get_session()
    token      = verify_otp_and_get_token(session_id)
    return token
