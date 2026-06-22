from openai import OpenAI
from config import OPENAI_API_KEY


class Assistant:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.messages = [
            {
                "role": "system",
                "content": (
                    "คุณคือ AI assistant ที่พูดภาษาไทย "
                    "ตอบสั้นกระชับ เหมาะสำหรับการสนทนาด้วยเสียง "
                    "ไม่ต้องใช้ markdown หรือ formatting ใดๆ"
                ),
            }
        ]

    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages,
            max_tokens=300,
        )

        reply = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def clear_history(self):
        self.messages = [self.messages[0]]
