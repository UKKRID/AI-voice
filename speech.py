import os
import asyncio
import tempfile
import struct
import threading
import edge_tts
import pygame
import speech_recognition as sr
from config import TTS_RATE, TTS_VOICE, STT_LANGUAGE, STT_TIMEOUT, MIC_DEVICE_INDEX

_speaking_lock = threading.Event()


def is_speaking():
    return _speaking_lock.is_set()


def set_speaking(val: bool):
    if val:
        _speaking_lock.set()
    else:
        _speaking_lock.clear()


class SpeechEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(device_index=MIC_DEVICE_INDEX)
        pygame.mixer.init()

    @staticmethod
    def _peak(data):
        count = len(data) // 2
        if count == 0:
            return 0
        shorts = struct.unpack(f"<{count}h", data)
        return max(abs(s) for s in shorts)

    def listen(self, language: str | None = None) -> str | None:
        lang = language or STT_LANGUAGE
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                threshold = self.recognizer.energy_threshold

                chunk = source.CHUNK
                sample_rate = source.SAMPLE_RATE
                sample_width = source.SAMPLE_WIDTH
                frames = []
                silence_chunks = 0
                has_speech = False
                max_chunks = int(sample_rate * 10 / chunk)
                silence_limit = int(sample_rate * 2.0 / chunk)

                for _ in range(max_chunks):
                    if is_speaking():
                        frames.clear()
                        has_speech = False
                        silence_chunks = 0
                        continue

                    data = source.stream.read(chunk)
                    peak = self._peak(data)
                    frames.append(data)

                    if is_speaking():
                        frames.clear()
                        has_speech = False
                        continue

                    if peak > threshold * 1.2:
                        has_speech = True
                        silence_chunks = 0
                    elif has_speech:
                        silence_chunks += 1
                        if silence_chunks >= silence_limit:
                            break

                if not frames or not has_speech:
                    return None

                audio_data = sr.AudioData(b"".join(frames), sample_rate, sample_width)
                text = self.recognizer.recognize_google(audio_data, language=lang)
                return text.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None
        except Exception:
            return None

    def speak(self, text: str):
        try:
            set_speaking(True)
            path = os.path.join(tempfile.gettempdir(), "ai_voice.mp3")
            rate_str = f"+{TTS_RATE - 180}%"
            asyncio.run(edge_tts.Communicate(text, TTS_VOICE, rate=rate_str).save(path))
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
            pygame.mixer.music.unload()
        except Exception:
            pass
        finally:
            set_speaking(False)
