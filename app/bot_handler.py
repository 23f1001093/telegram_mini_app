from fastapi import APIRouter , Request , HTTPException
from fastapi.responses import StreamingResponse
import io


from .call_handler import CallHandler
import asyncio
from fastapi import UploadFile, File
from .STT import STTClient
from .LLM import LLMClient
from .TTS import TTSClient

bot_router = APIRouter()
call_handler = CallHandler()
stt_client = STTClient()
llm_client = LLMClient()
tts_client = TTSClient()


@bot_router.post("/upload_voice")
async def upload_voice(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    transcript = stt_client.transcribe_audio(audio_bytes)
    llm_response = llm_client.generate_response(transcript)
    response_audio = tts_client.synthesize_speech(llm_response)
    
    return StreamingResponse(io.BytesIO(response_audio), media_type="audio/wav")





@bot_router.get("/start")
async def start():
    return {"message": "bot started"}

@bot_router.post("/update")
async def update(request: Request):
    data = await request.json()
    
    # Extract voice message from Telegram update
    voice = data.get("message", {}).get("voice")
    if not voice:
        return {"status": "ignored", "reason": "no voice message"}

    file_id= voice.get("file_id")
    if not file_id:
        raise HTTPException(status_code=400, detail="No file_id found in voice message")

    audio_bytes = await call_handler.download_telegram_file(file_id)

    # Simulate an async generator of audio chunks for CallHandler
    async def audio_stream():
      chunk_size = 4096
      for i in range(0, len(audio_bytes), chunk_size):
        yield audio_bytes[i:i+chunk_size]
        await asyncio.sleep(0)  # simulate network delay


    audio_response = await call_handler.handle_call(audio_stream())
    #send voice reply back to user
    chat_id = data["message"]["chat"]["id"]
    await call_handler.send_telegram_voice_message(chat_id, audio_response)

    return {"status": "success"}
