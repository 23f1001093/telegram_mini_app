from fastapi import APIRouter , Request

from .telegram_api import download_telegram_file , send_telegram_voice_message
from .config import Config

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}"

from .STT import STTClient
from .LLM import LLMClient
from .TTS import TTSClient

 

stt_client = STTClient()
llm_client = LLMClient()
tts_client = TTSClient()

webhook_router = APIRouter()

@webhook_router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    
    
    # 1. Extract voice/audio file ID from Telegram update
    voice= data.get("message", {}).get("voice",{})
    if not voice:
        return {"status": "no voice message received"}

    file_id = voice.get("file_id")    

    # 2. Download the audio file from Telegram servers
    audio_bytes = await download_telegram_file(file_id) 

    transcript = stt_client.transcribe_audio(audio_bytes)

    # 3. get LLM response
    llm_response = llm_client.generate_response(transcript)

    # 4. convert LLM text response to speech
    audio_response = tts_client.synthesize_speech(llm_response)

    # 5. send audio response as voice message  back to user via Telegram API
    await send_telegram_voice_message(chat_id=data["message"]["chat"]["id"], audio_bytes=audio_response)        

    return {"status": "success"}







