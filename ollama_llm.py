# ollama_llm.py
import requests
import json


class OllamaLLM:
    def __init__(self, model="llama3.2", temperature=0.0, max_tokens=250):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def __call__(self, prompt: str, session_id=None):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if session_id:
            payload["session_id"] = session_id

        try:
            res = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                stream=True
            )
            res.raise_for_status()

            full = ""

            for line in res.iter_lines():
                if not line:
                    continue

                try:
                    obj = json.loads(line.decode("utf-8"))
                    chunk = obj.get("response")
                    if chunk:
                        full += chunk
                except:
                    continue

            return full.strip()

        except Exception as e:
            return f"[Ollama Error] {e}"
