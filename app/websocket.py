import os
import asyncio
from fastapi import APIRouter, WebSocket
from .STT import STTClient
from .LLM import LLMClient
from .TTS import TTSClient
from pydub import AudioSegment
import numpy as np
import wave
import io
from dotenv import load_dotenv
from starlette.websockets import WebSocketDisconnect

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
    if header == b'\x1a\x45\xdf\xa3':
        return "webm"
    if header == b'RIFF':
        return "wav"
    if header == b'OggS':
        return "ogg"
    if header[:3] == b'ID3' or header[:2] == b'\xff\xfb':
        return "mp3"
    try:
        sample_size = min(len(data), 400)
        test_array = np.frombuffer(data[:sample_size], dtype=np.float32)
        max_val = np.max(np.abs(test_array))
        if 0.001 < max_val < 10.0:
            return "float32"
    except Exception:
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
    CHUNKS_TO_PROCESS = 50  # You might want 1 for single full utterance mode!
    first_format = None
    try:
        while True:
            try:
                audiobytes = await websocket.receive_bytes()
            except WebSocketDisconnect as ws_e:
                print(f"WebSocket disconnected: {ws_e}")
                break  # Client disconnected, exit loop.
            if chunk_count == 0:
                first_format = detect_audio_format(audiobytes)
                print(f"[DEBUG] Detected audio format: {first_format}")
            audio_buffer.append(audiobytes)
            chunk_count += 1
            if chunk_count >= CHUNKS_TO_PROCESS:
                if first_format == "webm":
                    audio_to_process = audio_buffer[0]
                else:
                    audio_to_process = b''.join(audio_buffer)

                # Convert input to WAV for STT
                try:
                    wav_bytes = convert_to_wav(audio_to_process, first_format)
                except Exception as e:
                    await websocket.send_text(f"Audio conversion failed: {e}")
                    audio_buffer, chunk_count, first_format = [], 0, None
                    continue
                
                # Save the audio for inspection
                with open("debug_browser_audio.wav", "wb") as f:
                    f.write(wav_bytes)
                print("Saved debug_browser_audio.wav for inspection")

                transcript = stt_client.transcribe_audio(wav_bytes)
                print(f"[DEBUG] Transcript: '{transcript}'")
                await websocket.send_text(f"Transcript: {transcript}")

                if not transcript or not transcript.strip():
                    await websocket.send_text("No speech detected, please speak clearly and try again.")
                    audio_buffer, chunk_count, first_format = [], 0, None
                    continue

                llm_response = llm_client.generate_response(transcript)
                print(f"[DEBUG] LLM reply: '{llm_response}'")
                await websocket.send_text(f"Bot reply: {llm_response}")

                if not llm_response or not llm_response.strip():
                    await websocket.send_text("Bot could not generate a reply, please try again.")
                    audio_buffer, chunk_count, first_format = [], 0, None
                    continue

                try:
                    reply_audio_bytes = tts_client.synthesize_speech(llm_response)
                except ValueError as tts_err:
                    await websocket.send_text(str(tts_err))
                    audio_buffer, chunk_count, first_format = [], 0, None
                    continue
                except Exception as tts_unexp:
                    await websocket.send_text(f"TTS failed: {tts_unexp}")
                    audio_buffer, chunk_count, first_format = [], 0, None
                    continue

                await websocket.send_bytes(reply_audio_bytes)
                await websocket.send_text("Reply finished!")

                audio_buffer, chunk_count, first_format = [], 0, None
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_text(f"WebSocket error: {e}")
        except Exception:
            pass  # Don't crash if already disconnected
    finally:
        try:
            await websocket.close()
        except Exception:
            pass  # Already closed
