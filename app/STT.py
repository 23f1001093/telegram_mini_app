import vosk
import wave
import json
import os
import tempfile

class STTClient:
    def __init__(self, model_path=None):
        """
        model_path: Path to the Vosk model directory (unzipped). 
        Example: 'model-en-us' for English, 'model-hi' for Hindi, etc.
        """
        self.model_path = model_path or os.getenv("VOSK_MODEL_PATH", "model-en-us")
        if not os.path.exists(self.model_path):
            raise ValueError(f"Vosk model directory not found: {self.model_path}")
        print(f"Loaded Vosk model from {self.model_path}")
        self.model = vosk.Model(self.model_path)

    def transcribe_audio(self, audio_bytes: bytes):
        """
        Transcribe WAV audio bytes using Vosk.
        """
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmpf:
            tmpf.write(audio_bytes)
            tmpf.flush()
            wf = wave.open(tmpf.name, "rb")
            rec = vosk.KaldiRecognizer(self.model, wf.getframerate())
            transcript = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    part = json.loads(rec.Result())
                    transcript += " " + part.get("text", "")
            transcript += " " + json.loads(rec.FinalResult()).get("text", "")
            wf.close()
        return transcript.strip()
