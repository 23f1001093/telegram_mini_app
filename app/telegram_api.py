import httpx
from .config import Config


TELEGRAM_API_BASE = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}"

async def download_telegram_file(file_id: str) -> bytes:
    async with httpx.AsyncClient() as client:
        # Step 1: Get file path
        response = await client.get(f"{TELEGRAM_API_BASE}/getFile", params={"file_id": file_id})
        response.raise_for_status()
        file_path = response.json()["result"]["file_path"]

        # Step 2: Download the file
        file_url = f"https://api.telegram.org/file/bot{Config.TELEGRAM_BOT_TOKEN}/{file_path}"
        file_response = await client.get(file_url)
        file_response.raise_for_status()
        return file_response.content
    

async def send_telegram_voice_message(chat_id: int, audio_bytes: bytes):
    async with httpx.AsyncClient() as client:
        files = {
            "voice": ("voice.ogg", audio_bytes, "audio/ogg")
        }
        data = {
            "chat_id": chat_id
        }
        response = await client.post(f"{TELEGRAM_API_BASE}/sendVoice", data=data, files=files)
        response.raise_for_status()
        return response.json()