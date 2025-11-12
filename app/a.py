from STT import STTClient  # or use correct import if your file/dir structure is different

stt_client = STTClient(model_path="/Users/aditiprasad/desktop/sirius/app/model-en-us/vosk-model-small-en-us-0.15")

with open('test.wav', 'rb') as f:
    result = stt_client.transcribe_audio(f.read())
    print(f"Transcript: {result}")