from gtts import gTTS
from pydub import AudioSegment
import io

class TTSClient:
    def __init__(self, lang="en"):
        self.lang = lang  # Set to "hi" for Hindi, etc.

    def synthesize_speech(self, text):
        """
        Synchronous: Convert text to WAV bytes (for sending as Telegram voice).
        """
        # Step 1: Generate MP3 in memory
        tts = gTTS(text=text, lang=self.lang)
        mp3_bytesio = io.BytesIO()
        tts.write_to_fp(mp3_bytesio)
        mp3_bytesio.seek(0)

        # Step 2: Convert MP3 to WAV in memory
        audio = AudioSegment.from_file(mp3_bytesio, format="mp3")
        wav_bytesio = io.BytesIO()
        # Telegram prefers monocodal, 16kHz PCM WAV:
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_bytesio, format="wav")
        wav_bytesio.seek(0)
        return wav_bytesio.getvalue()

    def save_audio(self, audio_bytes, filename="output.wav"):
        with open(filename, "wb") as f:
            f.write(audio_bytes)
