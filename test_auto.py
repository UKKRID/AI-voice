import sys
import io
import time
import json
import requests
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOOL_DESC = """คุณมีเครื่องมือเหล่านี้:
- get_time(): ดูเวลาปัจจุบัน
- get_date(): ดูวันที่ปัจจุบัน
- get_weather(): ดูสภาพอากาศ
- calculate(expression): คำนวณค่า เช่น calculate(2+3*4)
เมื่อต้องการใช้เครื่องมือ ให้ตอบในรูปแบบ: [tool:name] หรือ [tool:name:args]
ตอบสั้นกระชับ 1-2 ประโยค ไม่ต้องใช้ markdown"""

TESTS = [
    {"q": "สวัสดี", "expect": "greeting"},
    {"q": "วันนี้วันที่เท่าไหร่", "expect": "tool:get_date"},
    {"q": "ตอนนี้กี่โมง", "expect": "tool:get_time"},
    {"q": "2+3 เท่ากับเท่าไหร่", "expect": "tool:calculate"},
    {"q": "อากาศวันนี้เป็นยังไง", "expect": "tool:get_weather"},
    {"q": "โดเรมอนคืออะไร", "expect": "knowledge"},
    {"q": "เล่าเรื่องตลกหน่อย", "expect": "creative"},
    {"q": "เมืองหลวงของไทยคืออะไร", "expect": "knowledge"},
    {"q": "100*5 เท่ากับเท่าไหร่", "expect": "tool:calculate"},
    {"q": "ขอบคุณมาก", "expect": "greeting"},
    {"q": "วันนี้อากาศดีไหม", "expect": "tool:get_weather"},
    {"q": "50/2 เท่ากับเท่าไหร่", "expect": "tool:calculate"},
]

def test_llm(question):
    messages = [
        {"role": "system", "content": TOOL_DESC},
        {"role": "user", "content": question},
    ]
    start = time.time()
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
    )
    elapsed = time.time() - start
    data = resp.json()
    reply = data["message"]["content"]
    return elapsed, reply

results = []
print("=" * 60)
print("  Automated Test - 12 scenarios")
print("=" * 60)

for i, test in enumerate(TESTS):
    elapsed, reply = test_llm(test["q"])
    has_tool = "[tool:" in reply or "[tool" in reply
    is_short = len(reply) < 200
    passed = is_short and (not has_tool or "tool" in test["expect"])

    results.append({
        "q": test["q"],
        "time": elapsed,
        "reply": reply[:100],
        "has_tool": has_tool,
        "pass": passed,
    })

    status = "\033[92mPASS\033[0m" if passed else "\033[91mFAIL\033[0m"
    print(f"\n  #{i+1} {status} ({elapsed:.1f}s)")
    print(f"  Q: {test['q']}")
    print(f"  A: {reply[:100]}")

avg_time = sum(r["time"] for r in results) / len(results)
pass_count = sum(1 for r in results if r["pass"])

print("\n" + "=" * 60)
print(f"  Results: {pass_count}/{len(results)} passed")
print(f"  Avg time: {avg_time:.2f}s")
print(f"  Tool usage: {sum(1 for r in results if r['has_tool'])}/{len(results)}")
print("=" * 60)
