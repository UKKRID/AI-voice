import time
import speech_recognition as sr
from config import WAKE_WORD
from speech import SpeechEngine
from assistant import Assistant


def listen_for_wake_word(speech: SpeechEngine) -> bool:
    print(f"ฟังอยู่... (พูด '{WAKE_WORD}' เพื่อเริ่ม)")
    text = speech.listen()
    if text and WAKE_WORD in text:
        print(f"พบ wake word: {text}")
        return True
    return False


def main():
    print("=" * 50)
    print("AI Voice Assistant")
    print(f"Wake word: '{WAKE_WORD}'")
    print("พูด 'หยุด' หรือ 'exit' เพื่อออก")
    print("=" * 50)

    speech = SpeechEngine()
    assistant = Assistant()

    speech.speak("สวัสดีค่ะ พร้อมรับคำสั่งแล้ว")

    while True:
        try:
            if not listen_for_wake_word(speech):
                continue

            speech.speak("ฟังอยู่ค่ะ")

            user_input = speech.listen()
            if not user_input:
                speech.speak("ไม่ได้ยินค่ะ ลองพูดใหม่อีกครั้ง")
                continue

            print(f"คุณ: {user_input}")

            if user_input in ["หยุด", "exit", "ออก", "บาย"]:
                speech.speak("ลาก่อนค่ะ")
                break

            if user_input in ["ล้าง", "clear", "เริ่มใหม่"]:
                assistant.clear_history()
                speech.speak("ล้างประวัติแล้วค่ะ")
                continue

            reply = assistant.chat(user_input)
            print(f"AI: {reply}")
            speech.speak(reply)

        except KeyboardInterrupt:
            print("\nหยุดทำงาน")
            speech.speak("ลาก่อนค่ะ")
            break
        except Exception as e:
            print(f"Error: {e}")
            speech.speak("เกิดข้อผิดพลาดค่ะ")


if __name__ == "__main__":
    main()
