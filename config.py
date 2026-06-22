import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b")

WAKE_WORDS = [w.strip().lower() for w in os.getenv("WAKE_WORDS", "hi bonus,hey computer,hello ai").split(",")]
MIC_DEVICE_INDEX = int(os.getenv("MIC_DEVICE_INDEX", "1"))

TTS_RATE = 180
TTS_VOLUME = 1.0
TTS_VOICE = os.getenv("TTS_VOICE", "th-TH-PremwadeeNeural")
STT_LANGUAGE = "th-TH"
STT_TIMEOUT = 5
