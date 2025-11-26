# ollama_client.py
import os
import requests
from typing import Optional

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))

def generate(prompt: str,
             session_id: Optional[str] = None,
             max_tokens: int = 300,
             temperature: float = 0.0) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }
    if session_id:
        payload["session_id"] = session_id

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return f"[OLLAMA ERROR] {e}"

    # normalize response
    if isinstance(data, dict):
        for k in ("text", "response", "result"):
            if k in data and isinstance(data[k], str):
                return data[k].strip()
        gens = data.get("generations") or data.get("choices")
        if isinstance(gens, list) and gens:
            first = gens[0]
            if isinstance(first, dict):
                for k in ("text", "response"):
                    if k in first and isinstance(first[k], str):
                        return first[k].strip()
    return str(data)
