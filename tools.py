# tools.py
import json
import os
from typing import Tuple, List, Optional
from kb_index import query_kb
from ollama_llm import OllamaLLM
from prompts import SALES_MISSING_PROMPT, EXTRACT_FIELDS_PROMPT

LLM = OllamaLLM(max_tokens=200, temperature=0.0)

# canonical field list
REQUIRED_SALES_FIELDS = ["company_name", "team_size"]


def extract_json(text: str) -> dict:
    """Extract JSON portion from LLM output safely."""
    print("\n--- RAW LLM OUTPUT (SALES INFO) ---")
    print(text)
    print("-----------------------------------\n")
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {}


def kb_search_tool(message: str) -> str:
    return query_kb(message) or ""


# ------------------------------------------------------------
# Extract structured fields from a sales message
# ------------------------------------------------------------
def extract_sales_fields(message: str, session_id: str) -> dict:
    """
    Ask LLM to extract known fields from a single message.
    Always returns strings for values (empty string if not found).
    """
    prompt = EXTRACT_FIELDS_PROMPT.format(
        message=message,
        fields=", ".join(REQUIRED_SALES_FIELDS)
    )

    raw = LLM(prompt, session_id=session_id)
    data = extract_json(raw)

    out = {}
    for f in REQUIRED_SALES_FIELDS:
        v = data.get(f, "")
        # coerce to string safely
        if v is None:
            v = ""
        out[f] = str(v).strip()
    return out


# ------------------------------------------------------------
# SALES STORAGE (per-session)
# ------------------------------------------------------------
def save_sales_data(session_id: str, data: dict):
    os.makedirs("leads", exist_ok=True)
    path = f"leads/{session_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_sales_data(session_id: str) -> dict:
    path = f"leads/{session_id}.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # default template
    return {f: "" for f in REQUIRED_SALES_FIELDS}


# ------------------------------------------------------------
# FEATURE REQUEST STORAGE
# ------------------------------------------------------------
def save_feature_request(session_id: str, text: str):
    """Append feature requests per session."""
    os.makedirs("feature_requests", exist_ok=True)
    path = f"feature_requests/{session_id}.txt"
    with open(path, "a", encoding="utf-8") as f:
        f.write(text.strip() + "\n")


# ------------------------------------------------------------
# MISSING FIELDS PROMPT (LLM-driven)
# ------------------------------------------------------------
def sales_missing_info(message: str, session_id: str, fields: Optional[List[str]] = None) -> Tuple[List[str], str]:
    """
    Ask LLM which of the given fields are missing and return a follow-up question.
    - If `fields` is None, uses REQUIRED_SALES_FIELDS.
    - `fields` can be a list of field names to check / ask about.
    Returns: (missing_fields_list, followup_prompt)
    """
    if fields is None:
        fields = REQUIRED_SALES_FIELDS

    # ensure formatting is a comma separated string for the prompt
    fields_str = ", ".join(fields)

    prompt = SALES_MISSING_PROMPT.format(
        message=message,
        fields=fields_str
    )

    print("\n======= SALES MISSING PROMPT =======")
    print(prompt)
    print("====================================\n")

    raw = LLM(prompt, session_id=session_id)
    data = extract_json(raw)

    missing = data.get("missing_fields")
    follow = data.get("followup_prompt")

    # normalize outputs with safe fallbacks
    if not isinstance(missing, list):
        missing = list(fields)  # assume all requested are missing
    if not isinstance(follow, str):
        follow = f"Could you please provide {fields_str}?"

    print("👉 SALES MISSING:", missing)
    print("👉 FOLLOWUP:", follow)

    return missing, follow
