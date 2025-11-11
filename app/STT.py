import requests
import time
import os

class STTClient:
    def __init__(self):
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        self.upload_url = "https://api.assemblyai.com/v2/upload"
        self.transcript_url = "https://api.assemblyai.com/v2/transcript"
        self.headers = {
            "authorization": self.api_key,
        }

    def upload_audio(self, audio_bytes: bytes) -> str:
        response = requests.post(self.upload_url, headers=self.headers, data=audio_bytes)
        response.raise_for_status()
        return response.json()["upload_url"]

    def request_transcription(self, audio_url: str) -> str:
        json_data = {"audio_url": audio_url}
        response = requests.post(self.transcript_url, json=json_data, headers=self.headers)
        response.raise_for_status()
        return response.json()["id"]

    def get_transcription_result(self, transcript_id: str) -> str:
        url = f"{self.transcript_url}/{transcript_id}"
        while True:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if data["status"] == "completed":
                return data["text"]
            elif data["status"] == "error":
                raise Exception(f"Transcription error: {data['error']}")
            time.sleep(3)

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        upload_url = self.upload_audio(audio_bytes)
        transcript_id = self.request_transcription(upload_url)
        transcript_text = self.get_transcription_result(transcript_id)
        return transcript_text