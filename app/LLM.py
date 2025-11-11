import requests
import json
import os
class LLMClient:
    def __init__(self, endpoint_url="http://localhost:8000/llm", model="llama3.2"):
        self.endpoint_url = endpoint_url or os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
        self.model = model


    def generate_response(self, prompt):
        payload = {"model": self.model, "prompt": prompt}
        try:
            response = requests.post(self.endpoint_url, json=payload, timeout=120)
            response.raise_for_status()
            content = response.text
        # Collect and join all 'response' fields
            final_reply = []
            for line in content.strip().splitlines():
              try:
                obj = json.loads(line)
                if "response" in obj:
                    final_reply.append(obj["response"])
                if obj.get("done") is True:
                    break  # Stop at first completion
              except Exception:
                continue
            return "".join(final_reply)
        except Exception as e:
           return f"Ollama LLM error: {e}"
