# 1. Import the Ollama client and error class :contentReference[oaicite:0]{index=0}
from ollama import Client, ResponseError
from config import settings


def main():
    # 2. Instantiate the Ollama client targeting the local REST endpoint :contentReference[oaicite:1]{index=1}
    client = Client(host=settings.LLM_ENDPOINT)

    # 3. Verify the Ollama server is running by listing models :contentReference[oaicite:2]{index=2}
    try:
        models = client.list_models()
        print(f"Ollama is running. Available models: {[m.id for m in models]}")
    except Exception:
        # 4. Fallback: use the Ollama CLI via subprocess if SDK check fails :contentReference[oaicite:3]{index=3}
        import subprocess
        try:
            subprocess.run(["ollama", "list"], check=True, capture_output=True)
            print("Ollama CLI is available (server likely running).")
        except subprocess.CalledProcessError:
            print("ERROR: Ollama server is not running. Please start with `ollama serve`.")
            return

    # 5. Prompt the user for today’s task :contentReference[oaicite:4]{index=4}
    user_input = input("What do you want to do today?\n")

    # 6. Send the user input to the model for intent classification :contentReference[oaicite:5]{index=5}
    try:
        response = client.chat(
            model="deepseek-r1:8b",
            messages=[
                {"role": "system",  "content": "Classify intent as 'api testing' or 'front end testing'."},
                {"role": "user",    "content": user_input}
            ]
        )
        # 7. Extract and normalize the model’s reply :contentReference[oaicite:6]{index=6}
        intent = response.message.content.strip().lower()
        print(f"Detected intent: {intent}")
    except ResponseError as err:
        # 8. Handle Ollama HTTP/API errors gracefully :contentReference[oaicite:7]{index=7}
        print(f"Ollama error ({err.status_code}): {err.error}")

if __name__ == "__main__":
    main()
