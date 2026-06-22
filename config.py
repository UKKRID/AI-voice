import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WAKE_WORD = os.getenv("WAKE_WORD", "hey computer")

TTS_RATE = 180
TTS_VOLUME = 1.0
STT_LANGUAGE = "th-TH"
STT_TIMEOUT = 5
