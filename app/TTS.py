import requests
import os
from .config import Config

class TTSClient:
    def __init__(self):
        # Always prefer Config, fallback to env
        self.api_key = getattr(Config, "ELEVENLABS_API_KEY", None) or os.getenv("ELEVENLABS_API_KEY")

    def synthesize_speech(
        self,
        text,
        voice_id="21m00Tcm4TlvDq8ikWAM",
        optimization_level=2,
        output_format="mp3_44100_128",
        apply_text_normalization="auto"
    ):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.api_key,  # <- FIXED, removed quotes!
            "Accept": "audio/mpeg",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
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