import os
import re
import json
import datetime
import tempfile
import uuid
import sys
import io
import time
import requests
import edge_tts
import asyncio
import pygame
from queue import Queue, Empty
from threading import Thread
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, TTS_VOICE, TTS_RATE
from speech import set_speaking

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOOLS = {
    "get_time": lambda: datetime.datetime.now().strftime("%H:%M"),
    "get_date": lambda: datetime.datetime.now().strftime("%d/%m/%Y"),
    "get_weather": lambda: _get_weather(),
    "calculate": lambda expr: str(eval(expr)),
}

TOOL_DESC = """คุณมีเครื่องมือเหล่านี้:
- get_time(): ดูเวลาปัจจุบัน
- get_date(): ดูวันที่ปัจจุบัน
- get_weather(): ดูสภาพอากาศ
- calculate(expression): คำนวณค่า เช่น calculate(2+3*4)

เมื่อต้องการใช้เครื่องมือ ให้ตอบในรูปแบบ: [tool:name] หรือ [tool:name:args]
เช่น ถามว่าวันนี้วันอะไร ให้ตอบ [tool:get_date] แล้วรอรับค่า แล้วค่อยตอบเป็นประโยค
ตอบสั้นกระชับ 1-2 ประโยค ไม่ต้องใช้ markdown"""


def _get_weather():
    try:
        r = requests.get("https://wttr.in/?format=%C+%t+%h+%w&lang=th", timeout=5)
        return r.text.strip()
    except Exception:
        return "ไม่สามารถดูสภาพอากาศได้"


class Assistant:
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL.replace("/v1", "")
        self.messages = [
            {"role": "system", "content": TOOL_DESC},
        ]
        self._queue = Queue()
        self._tts_thread = Thread(target=self._tts_worker, daemon=True)
        self._tts_thread.start()

    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        reply = self._call_llm()

        attempts = 0
        while "[tool:" in reply and attempts < 5:
            reply = self._handle_tools(reply)
            attempts += 1

        self._queue.join()
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def _call_llm(self) -> str:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": self.messages,
                "stream": True,
            },
            stream=True,
        )

        full_reply = ""
        buffer = ""

        for line in response.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            token = chunk.get("message", {}).get("content", "")
            if not token:
                continue

            full_reply += token

            if re.search(r'\[tool', full_reply):
                continue

            buffer += token
            print(token, end="", flush=True)

            if re.search(r'[.!?\?]', buffer):
                self._speak(buffer.strip())
                buffer = ""

        if buffer.strip():
            self._speak(buffer.strip())

        return full_reply

    def _handle_tools(self, reply: str) -> str:
        tool_match = re.search(r'\[tool:(\w+)(?::([^\]]*))?\]', reply)
        if not tool_match:
            return reply

        tool_name = tool_match.group(1)
        tool_args = tool_match.group(2)

        result = ""
        if tool_name in TOOLS:
            if tool_args:
                result = TOOLS[tool_name](tool_args)
            else:
                result = TOOLS[tool_name]()
        else:
            result = f"ไม่รู้จักเครื่องมือ {tool_name}"

        self.messages.append({"role": "assistant", "content": reply})
        self.messages.append({"role": "user", "content": f"[ผลลัพธ์จาก {tool_name}]: {result}\n\nตอนนี้จงตอบผู้ใช้เป็นภาษาไทยตามปกติ ไม่ต้องใช้ tool อีก"})

        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": self.messages,
                "stream": True,
            },
            stream=True,
        )

        full_reply = ""
        buffer = ""

        for line in response.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            token = chunk.get("message", {}).get("content", "")
            if not token:
                continue

            full_reply += token
            buffer += token
            print(token, end="", flush=True)

            if re.search(r'[.!?\?]', buffer):
                self._speak(buffer.strip())
                buffer = ""

        if buffer.strip():
            self._speak(buffer.strip())

        return full_reply

    def _tts_worker(self):
        pygame.mixer.init()
        while True:
            try:
                text = self._queue.get(timeout=0.5)
            except Empty:
                continue
            try:
                set_speaking(True)
                uid = str(uuid.uuid4())[:8]
                path = os.path.join(tempfile.gettempdir(), f"ai_{uid}.mp3")
                rate_str = f"+{TTS_RATE - 180}%"
                asyncio.run(edge_tts.Communicate(text, TTS_VOICE, rate=rate_str).save(path))
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(50)
                pygame.mixer.music.unload()
                try:
                    os.remove(path)
                except OSError:
                    pass
            except Exception as e:
                print(f"  [TTS: {e}]", flush=True)
            finally:
                set_speaking(False)
                self._queue.task_done()

    def _speak(self, text: str):
        if text.strip():
            self._queue.put(text)

    def clear_history(self):
        self.messages = [self.messages[0]]
