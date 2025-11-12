import os
import asyncio
from fastapi import APIRouter, WebSocket
from .STT import STTClient
from .LLM import LLMClient
from .TTS import TTSClient
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Your chosen ElevenLabs voice

websocket_router = APIRouter()
stt_client = STTClient()
llm_client = LLMClient()
tts_client = TTSClient()

@websocket_router.websocket("/voice")
async def voice_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 1. Receive audio from frontend
            audio_bytes = await websocket.receive_bytes()
            print("Received audio chunk of length:", len(audio_bytes))

            # 2. Transcribe with ElevenLabs STT
            transcript = await stt_client.transcribe_audio(audio_bytes)
            print("Transcript:", transcript)
            await websocket.send_text(transcript)  # Optionally send to client

            # 3. Generate reply via LLM
            reply_text = llm_client.generate_response(transcript)
            print("Bot reply:", reply_text)

            # 4. Stream TTS reply back via ElevenLabs
            async for chunk in tts_client.stream_speech(reply_text, VOICE_ID):
                await websocket.send_bytes(chunk)

    except Exception as e:
        print("Error in websocket loop:", e)
        await websocket.close()
