from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import Optional

from .webhook_handler import webhook_router
from .bot_handler import bot_router
from .websocket import websocket_router

app = FastAPI()

app.include_router(webhook_router, prefix="/webhook")
app.include_router(bot_router, prefix="/bot")
app.include_router(websocket_router)



origins = [
    "http://localhost:8080",
    "https://web.telegram.org",
    "http://localhost:*",  # Allow any localhost port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for WebSocket (more permissive)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LLMRequest(BaseModel):
    model: Optional[str] = "llama3.1"  
    prompt: str

@app.post("/llm")
async def generate_llm_response(body: LLMRequest):
    ollama_url = "http://localhost:11434/api/generate"
    payload = {"model": body.model, "prompt": body.prompt}
    try:
        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        resp_json = response.json()
        answer = resp_json.get("response", "")
        return {"response": answer}
    except Exception as e:
        return {"response": f"Ollama call failed: {e}"}