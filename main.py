import time
from config import WAKE_WORDS
from speech import SpeechEngine
from assistant import Assistant

EXIT_WORDS = ["เลิกคุยกัน", "เลิกกัน", "หยุด", "exit", "ออก", "บาย"]
CLEAR_WORDS = ["ล้าง", "clear", "เริ่มใหม่"]


def match_intent(text, words):
    tokens = text.lower().split()
    return any(w in tokens for w in words)

BANNER = """
\033[96m    ___  ________  _________
   / _ |/ __/ _ \\ / __/ __/ 
  / __ / _// __ \\_\\ \\/__ \\  
 /_/ |_/___/_/ /_/\\___/___/  
\033[0m
\033[90m    AI Voice Assistant v1.0
    Local • Ollama • Thai\033[0m
"""

def ts():
    return time.strftime("\033[90m%H:%M:%S\033[0m")


def main():
    print(BANNER)
    print(f"  \033[90mWake word:\033[0m \033[93mbonus\033[0m")
    print(f"  \033[90mCommands:\033[0m \033[90m'เลิกคุยกัน' = exit, 'ล้าง' = clear\033[0m")
    print(f"  {'─' * 45}")
    print()

    speech = SpeechEngine()
    assistant = Assistant()

    speech.speak("พร้อมแล้วค่ะ")
    print(f"  {ts()} \033[92m●\033[0m \033[92mReady\033[0m")
    print()

    while True:
        try:
            print(f"  {ts()} \033[36m◉\033[0m \033[36mwaiting for wake word...\033[0m")
            text = speech.listen(language="en-US")
            if not text:
                continue

            found = any(w in text for w in WAKE_WORDS)
            if not found:
                continue

            print(f"  {ts()} \033[92m●\033[0m \033[92mWake word detected!\033[0m")
            speech.speak("ฟังอยู่ค่ะ")
            print(f"  {ts()} \033[93m▶\033[0m \033[93mConversation mode\033[0m \033[90m(p say 'เลิกคุยกัน' to exit)\033[0m")
            print()

            while True:
                user_input = speech.listen()
                if not user_input:
                    continue

                print(f"  {ts()} \033[37mYou:\033[0m {user_input}")

                if match_intent(user_input, EXIT_WORDS):
                    print(f"  {ts()} \033[91m■\033[0m \033[91mConversation ended\033[0m")
                    print()
                    speech.speak("ลาก่อนค่ะ")
                    break

                if match_intent(user_input, CLEAR_WORDS):
                    assistant.clear_history()
                    print(f"  {ts()} \033[93m●\033[0m \033[93mHistory cleared\033[0m")
                    speech.speak("ล้างประวัติแล้วค่ะ")
                    continue

                reply = assistant.chat(user_input)
                print()

        except KeyboardInterrupt:
            print(f"\n  {ts()} \033[91m●\033[0m \033[91mStopped\033[0m")
            speech.speak("ลาก่อนค่ะ")
            break
        except Exception as e:
            print(f"  {ts()} \033[91mError: {e}\033[0m")


if __name__ == "__main__":
    main()
