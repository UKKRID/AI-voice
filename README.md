# AI Voice Assistant

AI ช่วยเหลือที่สั่งงานด้วยเสียง รองรับภาษาไทย

## คุณสมบัติ

- Wake word detection: "hi bonus" (เปลี่ยนได้ใน .env)
- พูดคุยกับ AI ผ่านไมค์
- AI ตอบกลับเป็นเสียง
- ใช้ GPT-3.5-turbo

## ติดตั้ง

1. ติดตั้ง Python 3.10+
2. สร้าง virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. ติดตั้ง dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. ตั้งค่า API key:
   - คัดลอก `.env.example` เป็น `.env`
   - ใส่ OpenAI API key

5. รัน:
   ```bash
   python main.py
   ```

## วิธีใช้

1. รันโปรแกรม
2. พูด "hey computer" เพื่อปลุก
3. พูดคำสั่งหรือคำถาม
4. พูด "หยุด" หรือ "exit" เพื่อออก

## คำสั่งพิเศษ

- "ล้าง" / "clear" - ล้างประวัติสนทนา
- "หยุด" / "exit" - ออกจากโปรแกรม
