import sys
import io
import time
import json
import datetime
import requests
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOOL_DESC = (
    "คุณมีเครื่องมือ: get_time(), get_date(), get_weather(), calculate(expr) "
    "ตอบสั้น 1-2 ประโยค ไม่ต้องใช้ markdown"
)

TESTS = [
    "สวัสดี",
    "วันนี้วันที่เท่าไหร่",
    "ตอนนี้กี่โมง",
    "2+3 เท่ากับเท่าไหร่",
    "อากาศวันนี้เป็นยังไง",
    "โดเรมอนคืออะไร",
    "เล่าเรื่องตลกหน่อย",
    "เมืองหลวงของไทยคืออะไร",
    "100*5 เท่ากับเท่าไหร่",
    "ขอบคุณมาก",
    "วันนี้อากาศดีไหม",
    "50/2 เท่ากับเท่าไหร่",
]

log = []
round_num = 0

print("=" * 60)
print("  Continuous Test Loop - until 23:50")
print("=" * 60)

while True:
    now = datetime.datetime.now()
    if now.hour == 23 and now.minute >= 50:
        print("\nTime's up! Stopping...")
        break
    if now.hour == 0:
        print("\nMidnight! Stopping...")
        break

    round_num += 1
    round_pass = 0
    round_times = []
    ts = now.strftime("%H:%M:%S")
    print(f"\n--- Round {round_num} ({ts}) ---")

    for q in TESTS:
        start = time.time()
        try:
            resp = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": TOOL_DESC},
                        {"role": "user", "content": q},
                    ],
                    "stream": False,
                },
                timeout=30,
            )
            elapsed = time.time() - start
            reply = resp.json()["message"]["content"]
            ok = len(reply) < 200
            if ok:
                round_pass += 1
            round_times.append(elapsed)
            sym = "OK" if ok else "LONG"
            print(f"  [{sym}] {elapsed:5.1f}s | {q[:30]:30s} | {reply[:60]}")
        except Exception as e:
            elapsed = time.time() - start
            round_times.append(elapsed)
            print(f"  [ERR] {elapsed:5.1f}s | {q[:30]:30s} | {e}")

    avg = sum(round_times) / len(round_times) if round_times else 0
    log.append({
        "round": round_num,
        "time": ts,
        "pass": round_pass,
        "total": len(TESTS),
        "avg": round(avg, 2),
    })
    print(f"  -> {round_pass}/{len(TESTS)} pass, avg {avg:.2f}s")

    time.sleep(60)

print("\n" + "=" * 60)
print("  FINAL SUMMARY")
print("=" * 60)
if log:
    all_avg = sum(l["avg"] for l in log) / len(log)
    all_pass = sum(l["pass"] for l in log)
    all_total = sum(l["total"] for l in log)
    print(f"  Rounds: {len(log)}")
    print(f"  Total tests: {all_total}")
    print(f"  Pass rate: {all_pass}/{all_total} ({all_pass / all_total * 100:.0f}%)")
    print(f"  Avg time: {all_avg:.2f}s")
    print(f"  Best round: {min(l['avg'] for l in log):.2f}s")
    print(f"  Worst round: {max(l['avg'] for l in log):.2f}s")
print("=" * 60)
