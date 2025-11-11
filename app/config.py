import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into os.environ

class Config:
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")