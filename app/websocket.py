from fastapi import APIRouter, WebSocket
from .STT import STTClient
from .LLM import LLMClient
from .TTS import TTSClient
from .config import Config
import httpx

websocket_router = APIRouter()
stt_client = STTClient()
llm_client = LLMClient()
tts_client = TTSClient()

@websocket_router.websocket("/voice")
async def voice_ws(websocket: WebSocket):
    await websocket.accept()
   
    audio_chunks = []
    while True:
        try:
            data = await websocket.receive_bytes()
        except Exception:
            break  # socket closed, exit loop

        if not data:
            break
        print(f"Received audio chunk of size: {len(data)}") 
        audio_chunks.append(data)
        # Or stream to STT as they arrive, for end-to-end live conversation.

    # After audio sending completes:
    audio_bytes = b"".join(audio_chunks)
    transcript = stt_client.transcribe_audio(audio_bytes)
    print("Transcribed text:", transcript) 
    reply_text = llm_client.generate_response(transcript)
    print("Bot reply text:", reply_text)

    # REAL-TIME TTS RESPONSE BELOW:
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # use your preferred ElevenLabs voice
    api_key = Config.ELEVENLABS_API_KEY
    async for chunk in elevenlabs_stream_tts(reply_text, voice_id, api_key):
        await websocket.send_bytes(chunk)
    await websocket.close()
    print("Audio sending complete, connection closed.")

async def elevenlabs_stream_tts(text, voice_id, api_key):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    headers = {"xi-api-key": api_key, "Accept": "audio/mpeg"}
    data = {"text": text}
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", url, headers=headers, json=data) as resp:
            async for chunk in resp.aiter_bytes():
                yield chunk  # yield each audio chunk for streaming via websocket