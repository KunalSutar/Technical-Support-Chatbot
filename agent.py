# agent.py
import json
import re
from typing import Dict
from ollama_llm import OllamaLLM

from prompts import INTENT_PROMPT, DRAFT_RESPONSE_PROMPT, ESCALATION_PROMPT
from tools import (
    kb_search_tool,
    sales_missing_info,
    extract_sales_fields,
    load_sales_data,
    save_sales_data,
    save_feature_request,
    REQUIRED_SALES_FIELDS
)

LLM = OllamaLLM(max_tokens=400, temperature=0.0)


# ------------------------------------------------------------
# UNIVERSAL JSON CLEANER
# ------------------------------------------------------------
def extract_json(text: str) -> dict:
    print("\n--- RAW LLM OUTPUT ---")
    print(text)
    print("--- END RAW ---\n")
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {}


# ------------------------------------------------------------
# FINAL RESPONSE CLEANER
# ------------------------------------------------------------
def clean_final_response(raw: str) -> str:
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        data = json.loads(raw[start:end])
        if "response" in data:
            return data["response"].strip()
    except Exception:
        pass

    m = re.search(r'"response"\s*:\s*"([^"]+)"', raw, re.DOTALL)
    if m:
        return m.group(1).strip()

    return raw.strip()


# ------------------------------------------------------------
# INTENT CLASSIFICATION
# ------------------------------------------------------------
def classify_intent(msg: str, session_id: str) -> str:
    prompt = INTENT_PROMPT.format(message=msg)
    raw = LLM(prompt, session_id=session_id)
    data = extract_json(raw)
    return data.get("intent", "technical_support")


# ------------------------------------------------------------
# RESPONSE GENERATION
# ------------------------------------------------------------
def draft_response(intent, user_text, kb_snippet, missing_fields, followup_prompt, session_id) -> str:
    prompt = DRAFT_RESPONSE_PROMPT.format(
        intent=intent,
        kb_snippet=kb_snippet,
        missing_fields=missing_fields,
        followup_prompt=followup_prompt,
        message=user_text
    )
    raw = LLM(prompt, session_id=session_id)
    return clean_final_response(raw)


# ------------------------------------------------------------
# ESCALATION LOGIC
# ------------------------------------------------------------
def decide_escalation(msg, intent, kb_found, session_id) -> bool:
    prompt = ESCALATION_PROMPT.format(
        intent=intent,
        kb_found=str(kb_found).lower(),
        message=msg
    )
    raw = LLM(prompt, session_id=session_id)
    data = extract_json(raw)

    if intent == "human_request":
        return True
    return bool(data.get("escalate", False))


# ------------------------------------------------------------
# MAIN MESSAGE HANDLER
# ------------------------------------------------------------
def handle_message(user_text: str, session_id: str) -> Dict:
    print("\n===== NEW MESSAGE =====")
    print("SESSION:", session_id)
    print("USER:", user_text)
    print("========================\n")

    intent = classify_intent(user_text, session_id)

    kb_snippet = ""
    missing = []
    follow = ""

    # technical support -> KB lookup
    if intent == "technical_support":
        kb_snippet = kb_search_tool(user_text)

    # sales lead flow: LOAD -> EXTRACT -> SAVE -> compute missing -> ask only for missing
    if intent == "sales_lead":
        # load existing per-session values (may be empty)
        stored = load_sales_data(session_id)

        # extract whatever is present in THIS message
        extracted = extract_sales_fields(user_text, session_id)

        # update stored with any extracted non-empty values (iterate required fields)
        updated = False
        for f in REQUIRED_SALES_FIELDS:
            val = extracted.get(f)
            if val is not None and str(val).strip() != "":
                if stored.get(f, "") != str(val).strip():
                    stored[f] = str(val).strip()
                    updated = True

        # persist immediately so file always reflects latest inputs
        save_sales_data(session_id, stored)

        # compute what is still missing AFTER update
        missing = [f for f in REQUIRED_SALES_FIELDS if not stored.get(f)]

        # if any missing, ask LLM to craft a followup prompt specifically for them
        if missing:
            # sales_missing_info accepts fields override; pass missing list
            missing, follow = sales_missing_info(user_text, session_id, fields=missing)
        else:
            follow = ""

    # feature request -> append to session-specific file
    if intent == "feature_request":
        try:
            save_feature_request(session_id, user_text)
        except Exception as e:
            print("Failed to save feature request:", e)

    # generate assistant reply
    response = draft_response(
        intent=intent,
        user_text=user_text,
        kb_snippet=kb_snippet,
        missing_fields=missing,
        followup_prompt=follow,
        session_id=session_id
    )

    escalate = decide_escalation(user_text, intent, bool(kb_snippet), session_id)

    return {
        "classification": intent,
        "response": response,
        "escalate": escalate,
        "kb_snippet": kb_snippet,
        "missing_fields": missing,
        "followup_prompt": follow
    }
