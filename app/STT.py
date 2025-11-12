import os
import vosk
import wave
import json
import tempfile

class STTClient:
    """
    Speech-to-text using Vosk. Input: WAV audio bytes. Output: transcript string.
    """
    def __init__(self, model_path=None):
        self.model_path = model_path or os.getenv("VOSK_MODEL_PATH", "model-en-us/vosk-model-small-en-us-0.15")
        if not os.path.exists(self.model_path):
            raise ValueError(f"Vosk model directory not found: {self.model_path}")
        self.model = vosk.Model(self.model_path)

    def transcribe_audio(self, audio_bytes):
        """Transcribe WAV audio bytes to text using Vosk."""
        transcript = ""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmpf:
                tmpf.write(audio_bytes)
                tmpf.flush()
                with wave.open(tmpf.name, "rb") as wf:
                    rec = vosk.KaldiRecognizer(self.model, wf.getframerate())
                    while True:
                        data = wf.readframes(4000)
                        if len(data) == 0:
                            break
                        if rec.AcceptWaveform(data):
                            part = json.loads(rec.Result())
                            transcript += " " + part.get("text", "")
                    transcript += " " + json.loads(rec.FinalResult()).get("text", "")
        except Exception as e:
            # Catch and log audio decoding errors, return empty transcript for robustness
            print(f"[STTClient] Error transcribing audio: {e}")
            return ""
        return transcript.strip()