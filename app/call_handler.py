import asyncio
from .STT import STTClient
from.LLM import LLMClient
from .TTS import TTSClient

stt_client = STTClient()
llm_client = LLMClient()
tts_client = TTSClient()

class CallHandler:
    def __init__(self):
        self.audio_buffer = bytearray()
        self.transcript = ""

    async def recieve_audio_chunk(self, chunk :bytes):
        # Step 1: Transcribe audio to tex
        self.audio_buffer.extend(chunk)
    
    async def process_audio(self):
       # Convert buffered audio bytes to text
       self.transcript = stt_client.transcribe_audio(bytes(self.audio_buffer))
       return self.transcript
    
    async def generate_response(self):
        # Step 2: Get LLM response
        llm_response = llm_client.generate_response(self.transcript)
        return llm_response
    
    async def synthesize_speech(self, text: str):
        # Step 3: Convert LLM text response to speech
        audio_response = tts_client.synthesize_speech(text)
        return audio_response       
    
    async def handle_call(self, audio_stream_async_generator):
        async for chunk in audio_stream_async_generator:
            await self.recieve_audio_chunk(chunk)
        
        transcript = await self.process_audio()
        llm_response = await self.generate_response()
        audio_response = await self.synthesize_speech(llm_response)
        
        return audio_response   