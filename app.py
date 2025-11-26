# app.py
import streamlit as st
import requests
import uuid

API = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="NullAxis Agent", layout="centered")
st.title("NullAxis Customer Support Agent")

# Generate session ID ONCE
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


def call_backend(text):
    try:
        r = requests.post(
            API,
            data={
                "message": text,
                "session_id": st.session_state.session_id
            },
            timeout=60
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"response": f"[Backend Error] {e}"}


# Display previous messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])


# Chat input at bottom
user_input = st.chat_input("Type your message...")

if user_input:
    # User bubble
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Send to backend
    backend = call_backend(user_input)
    bot_reply = backend.get("response", "")

    # Bot bubble
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.write(bot_reply)
