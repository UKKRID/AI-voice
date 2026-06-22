import os
import sys
import io
import time
import json
import asyncio
import tempfile
import requests
import edge_tts
import pygame
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, TTS_VOICE, TTS_RATE

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TEST_QUESTIONS = [
    "สวัสดี",
    "วันนี้วันที่เท่าไหร่",
    "ตอนนี้กี่โมง",
    "2+3 เท่ากับเท่าไหร่",
    "อากาศวันนี้เป็นยังไง",
    "เล่าเรื่องตลกหน่อย",
    "โดเรมอนคืออะไร",
    "เมืองหลวงของไทยคืออะไร",
    "100*5 เท่ากับเท่าไหร่",
    "อากาศเป็นยังไงบ้าง",
]

TOOL_DESC = """คุณมีเครื่องมือเหล่านี้:
- get_time(): ดูเวลาปัจจุบัน
- get_date(): ดูวันที่ปัจจุบัน
- get_weather(): ดูสภาพอากาศ
- calculate(expression): คำนวณค่า เช่น calculate(2+3*4)
เมื่อต้องการใช้เครื่องมือ ให้ตอบในรูปแบบ: [tool:name] หรือ [tool:name:args]
ตอบสั้นกระชับ 1-2 ประโยค ไม่ต้องใช้ markdown"""


def test_tts(text="สวัสดีค่ะ ทดสอบเสียง"):
    start = time.time()
    path = os.path.join(tempfile.gettempdir(), "test_tts.mp3")
    asyncio.run(edge_tts.Communicate(text, TTS_VOICE).save(path))
    elapsed = time.time() - start
    size = os.path.getsize(path)
    os.remove(path)
    return elapsed, size


def test_llm(question):
    start = time.time()
    messages = [
        {"role": "system", "content": TOOL_DESC},
        {"role": "user", "content": question},
    ]
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
    )
    data = resp.json()
    reply = data["message"]["content"]
    elapsed = time.time() - start
    return elapsed, reply


def test_tts_playback(text="ทดสอบเสียง"):
    pygame.mixer.init()
    path = os.path.join(tempfile.gettempdir(), "test_play.mp3")
    asyncio.run(edge_tts.Communicate(text, TTS_VOICE).save(path))
    start = time.time()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(50)
    elapsed = time.time() - start
    pygame.mixer.music.unload()
    pygame.mixer.quit()
    os.remove(path)
    return elapsed


print("=" * 60)
print("  AI Voice Assistant - Performance Test")
print("=" * 60)

# Test 1: TTS generation
print("\n[1] TTS Generation (edge-tts)")
tts_times = []
for i in range(3):
    elapsed, size = test_tts()
    tts_times.append(elapsed)
    print(f"  #{i+1}: {elapsed:.2f}s ({size} bytes)")
avg_tts = sum(tts_times) / len(tts_times)
print(f"  Avg: {avg_tts:.2f}s")

# Test 2: TTS playback
print("\n[2] TTS Playback (pygame)")
play_times = []
for i in range(3):
    elapsed = test_tts_playback("ทดสอบเสียง 1 2 3")
    play_times.append(elapsed)
    print(f"  #{i+1}: {elapsed:.2f}s")
avg_play = sum(play_times) / len(play_times)
print(f"  Avg: {avg_play:.2f}s")

# Test 3: LLM response
print("\n[3] LLM Response (Ollama - gemma4:e4b)")
llm_times = []
llm_replies = []
for i, q in enumerate(TEST_QUESTIONS[:5]):
    elapsed, reply = test_llm(q)
    llm_times.append(elapsed)
    llm_replies.append(reply)
    print(f"  Q: {q}")
    print(f"  A: {reply[:80]}...")
    print(f"  Time: {elapsed:.2f}s")
avg_llm = sum(llm_times) / len(llm_times)
print(f"  Avg: {avg_llm:.2f}s")

# Test 4: Full pipeline simulation
print("\n[4] Full Pipeline (LLM + TTS)")
pipeline_times = []
for i, q in enumerate(TEST_QUESTIONS[:5]):
    t0 = time.time()
    elapsed_llm, reply = test_llm(q)
    t1 = time.time()
    asyncio.run(edge_tts.Communicate(reply, TTS_VOICE).save(os.path.join(tempfile.gettempdir(), "pipe.mp3")))
    t2 = time.time()
    total = t2 - t0
    pipeline_times.append({"q": q, "llm": elapsed_llm, "tts_gen": t2-t1, "total": total})
    print(f"  Q: {q}")
    print(f"  LLM: {elapsed_llm:.2f}s | TTS: {t2-t1:.2f}s | Total: {total:.2f}s")

avg_pipeline = sum(p["total"] for p in pipeline_times) / len(pipeline_times)
print(f"  Avg total: {avg_pipeline:.2f}s")

# Summary
print("\n" + "=" * 60)
print("  SUMMARY")
print("=" * 60)
print(f"  TTS generation:    {avg_tts:.2f}s avg")
print(f"  TTS playback:      {avg_play:.2f}s avg")
print(f"  LLM response:      {avg_llm:.2f}s avg")
print(f"  Full pipeline:     {avg_pipeline:.2f}s avg")
print(f"  Human-like target: < 3s")
status = "PASS" if avg_pipeline < 5 else "NEEDS IMPROVEMENT"
print(f"  Status:            {status}")
print("=" * 60)
