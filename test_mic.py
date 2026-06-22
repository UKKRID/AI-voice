import speech_recognition as sr
import wave
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

r = sr.Recognizer()
mic = sr.Microphone(device_index=14)

print("=== Recording Test ===")
print("Speak 'hi bonus' clearly into mic NOW (5 seconds)...")
with mic as source:
    r.adjust_for_ambient_noise(source, duration=2)
    print(f"Threshold: {r.energy_threshold}")
    r.energy_threshold = max(r.energy_threshold * 0.5, 50)
    print(f"Adjusted threshold: {r.energy_threshold}")
    audio = r.listen(source, timeout=10, phrase_time_limit=10)

print(f"Recorded: {len(audio.frame_data)} bytes, {audio.sample_rate}Hz")

# Save to WAV
with wave.open("test_recording.wav", "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(audio.sample_width)
    wf.setframerate(audio.sample_rate)
    wf.writeframes(audio.frame_data)
print("Saved to test_recording.wav")

# Try recognition with show_all
print("\nSending to Google...")
result = r.recognize_google(audio, language="en-US", show_all=True)
print(f"Google result: {result}")

result_th = r.recognize_google(audio, language="th-TH", show_all=True)
print(f"Google TH result: {result_th}")
