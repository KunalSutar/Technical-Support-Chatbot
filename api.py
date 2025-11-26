# api.py
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from agent import handle_message
from kb_index import build_index

app = FastAPI()


@app.on_event("startup")
def startup():
    build_index("kb")


@app.post("/chat")
async def chat(
    message: str = Form(...),
    session_id: str = Form(...)
):
    result = handle_message(message, session_id=session_id)
    return JSONResponse(result)
