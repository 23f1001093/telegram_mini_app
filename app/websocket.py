import os
import asyncio
from fastapi import APIRouter, WebSocket
from .STT import STTClient    # <-- Vosk STT!
from .LLM import LLMClient
from .TTS import TTSClient
from pydub import AudioSegment
import numpy as np
import wave
import io
from dotenv import load_dotenv

load_dotenv()

VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
websocket_router = APIRouter()
stt_client = STTClient(model_path="/Users/aditiprasad/desktop/sirius/app/model-en-us/vosk-model-small-en-us-0.15")

llm_client = LLMClient()
tts_client = TTSClient()

def detect_audio_format(data: bytes) -> str:
    if len(data) < 4:
        return "float32"
    header = data[:4]
    if header[:4] == b'\x1a\x45\xdf\xa3':
        return "webm"
    if header[:4] == b'RIFF':
        return "wav"
    if header[:4] == b'OggS':
        return "ogg"
    if header[:3] == b'ID3' or header[:2] == b'\xff\xfb':
        return "mp3"
    try:
        sample_size = min(len(data), 400)
        test_array = np.frombuffer(data[:sample_size], dtype=np.float32)
        max_val = np.max(np.abs(test_array))
        if 0.001 < max_val < 10.0:
            return "float32"
    except:
        pass
    return "float32"

def convert_to_wav(audio_data: bytes, format_hint: str = None) -> bytes:
    if format_hint is None:
        format_hint = detect_audio_format(audio_data)
    try:
        if format_hint == "webm":
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
            out_io = io.BytesIO()
            audio.export(out_io, format="wav", parameters=["-ar", "16000", "-ac", "1"])
            out_io.seek(0)
            return out_io.getvalue()
        elif format_hint == "float32":
            remainder = len(audio_data) % 4
            if remainder != 0:
                padding = 4 - remainder
                audio_data += b'\x00' * padding
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            audio_array = np.nan_to_num(audio_array, nan=0.0, posinf=0.0, neginf=0.0)
            audio_array = np.clip(audio_array, -1.0, 1.0)
            audio_int16 = (audio_array * 32767).astype(np.int16)
            out_io = io.BytesIO()
            with wave.open(out_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(audio_int16.tobytes())
            out_io.seek(0)
            return out_io.getvalue()
        elif format_hint in ["wav", "ogg", "mp3"]:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=format_hint)
            out_io = io.BytesIO()
            audio.export(out_io, format="wav", parameters=["-ar", "16000", "-ac", "1"])
            out_io.seek(0)
            return out_io.getvalue()
        else:
            raise Exception(f"Unsupported format: {format_hint}")
    except Exception as e:
        raise Exception(f"Could not convert audio: {e}")

@websocket_router.websocket("/voice")
async def voice_ws(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = []
    chunk_count = 0
    CHUNKS_TO_PROCESS = 50
    first_format = None
    try:
        while True:
            audiobytes = await websocket.receive_bytes()
            if chunk_count == 0:
                first_format = detect_audio_format(audiobytes)
            audio_buffer.append(audiobytes)
            chunk_count += 1
            if chunk_count >= CHUNKS_TO_PROCESS:
                if first_format == "webm":
                    audio_to_process = audio_buffer[0]
                else:
                    audio_to_process = b''.join(audio_buffer)
                wav_bytes = convert_to_wav(audio_to_process, first_format)
                # --- LOCAL/STT --- #
                transcript = stt_client.transcribe_audio(wav_bytes)
                await websocket.send_text(f"Transcript: {transcript}")
                # --- LLM Logic --- #
                llm_response = llm_client.generate_response(transcript)
                await websocket.send_text(f"Bot reply: {llm_response}")
                # --- TTS (ElevenLabs) --- #
                async for tts_chunk in tts_client.stream_speech(llm_response, VOICE_ID):
                    await websocket.send_bytes(tts_chunk)
                await websocket.send_text("Reply finished!")
                audio_buffer = []
                chunk_count = 0
                first_format = None
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
