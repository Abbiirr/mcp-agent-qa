# Example fix for client.py
from ollama import Client
from config import settings

def get_ollama_client():
    try:
        # Make sure we're using the correct URL format
        client = Client(host=settings.LLM_ENDPOINT)
        # Test the connection with a simple API call
        client.list()
        return client
    except Exception as e:
        raise RuntimeError(f"ERROR: Ollama server is not running. Please start it with `ollama serve`. Details: {str(e)}")