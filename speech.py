import speech_recognition as sr
import pyttsx3
from config import TTS_RATE, TTS_VOLUME, STT_LANGUAGE, STT_TIMEOUT


class SpeechEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", TTS_RATE)
        self.tts.setProperty("volume", TTS_VOLUME)
        self.microphone = sr.Microphone()

    def listen(self) -> str | None:
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=STT_TIMEOUT)
                text = self.recognizer.recognize_google(audio, language=STT_LANGUAGE)
                return text.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

    def speak(self, text: str):
        self.tts.say(text)
        self.tts.runAndWait()
