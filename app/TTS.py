import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class TTSClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY must be set in .env or passed explicitly.")

    # ASYNC STREAMING METHOD (for real-time bots/frontends)
    async def stream_speech(
        self,
        text,
        voice_id="21m00Tcm4TlvDq8ikWAM",
        model_id="eleven_multilingual_v2"
    ):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        headers = {
            "xi-api-key": self.api_key,
            "Accept": "audio/wav"
        }
        payload = {
            "text": text,
            "model_id": model_id,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as resp:
                if resp.status_code != 200:
                    details = await resp.aread()
                    print("ElevenLabs Streaming TTS Error:", resp.status_code, details)
                    return
                async for chunk in resp.aiter_bytes():
                    yield chunk  # For use in: async for chunk in tts_client.stream_speech(...)

    # SYNCHRONOUS METHOD (for saving full audio files)
    def synthesize_speech(
        self,
        text,
        voice_id="21m00Tcm4TlvDq8ikWAM",
        model_id="eleven_multilingual_v2",
        optimization_level=2,
        output_format="mp3_44100_128",
        apply_text_normalization="auto"
    ):
        import requests  # only needed here
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Accept": "audio/wav",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": model_id,
            "optimization_level": optimization_level,
            "output_format": output_format,
            "apply_text_normalization": apply_text_normalization
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.content

    def save_audio(self, audio_bytes, filename="output.mp3"):
        with open(filename, "wb") as f:
            f.write(audio_bytes)
