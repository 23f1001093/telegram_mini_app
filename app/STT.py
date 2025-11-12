import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class STTClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY must be set in .env or passed.")

        self.url = "https://api.elevenlabs.io/v1/speech-to-text"
        self.headers = {
            "xi-api-key": self.api_key,
            # ElevenLabs STT is typically audio/wav and may require content type on upload
        }

    async def transcribe_audio(self, audio_bytes: bytes, mime_type="audio/wav") -> str:
        """
        Upload audio bytes (wav or mp3) to ElevenLabs STT and return transcript.
        """
        files = {"audio": ("audio.wav", audio_bytes, mime_type)}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self.url, headers=self.headers, files=files)
            response.raise_for_status()
            data = response.json()
            # Adjust key if the ElevenLabs response changes format
            return data.get("transcript") or data.get("text") or str(data)
