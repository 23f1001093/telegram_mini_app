import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class TTSClient:
    def __init__(self, api_key=None, voice_id=None, model_id="eleven_multilingual_v2"):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        print(f"Using API key: {self.api_key}")
        self.voice_id = voice_id or "21m00Tcm4TlvDq8ikWAM"
        self.model_id = model_id
        if not self.api_key:
            raise ValueError("Set ELEVENLABS_API_KEY in .env or pass in init.")

    def synthesize_speech(self, text, output_format="mp3_44100_128"):
        if not text or not text.strip():
            raise ValueError("TTS input text is empty! Provide actual transcript.")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": self.model_id,
            "language_code": "en",
            "voice_settings": { "stability": 0.5, "similarity_boost": 0.75 },
            "output_format": output_format,
            "pronunciation_dictionary_locators": [],
            "seed": None,
            "previous_text": None,
            "next_text": None,
            "previous_request_ids": [],
            "next_request_ids": [],
            "use_pvc_as_ivc": False,
            "apply_text_normalization": "off",
            "apply_language_text_normalization": "off",
            "hcaptcha_token": None
        }
        print(json.dumps(payload, indent=2))  
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.content