import os
from config import Config
try:
    from config import ELEVENLABS_API_KEY
except ImportError:
    # If your Config is a class, adjust accordingly:
    # from Config import Config
    # ELEVENLABS_API_KEY = Config.ELEVENLABS_API_KEY
    ELEVENLABS_API_KEY = None

print("From Config:")
print(f"ELEVENLABS_API_KEY = '{ELEVENLABS_API_KEY}'")

# Also test environment variable directly (if that's how it's set)
env_key = os.getenv("ELEVENLABS_API_KEY")
print("From environment:")
print(f"ELEVENLABS_API_KEY (env) = '{env_key}'")

import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("ELEVENLABS_API_KEY"))
print(os.getenv("OLLAMA_API_URL"))
exit()