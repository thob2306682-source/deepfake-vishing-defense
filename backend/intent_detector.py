"""
Module: backend/intent_detector.py (Phụ trách: Thành viên B - Task B04 & B05)
Chức năng:
  - Chuyển đổi file âm thanh thành văn bản (Speech-to-Text) hoặc nhận transcript.
  - Quét danh sách từ khóa nhạy cảm Tiếng Việt & Tiếng Anh (chuyển khoản, số tài khoản,
    chuyển gấp, bí mật, wire transfer, urgent...).
  - Đánh dấu tô sáng (<mark>) các từ khóa nhạy cảm để hiển thị trên SOC Dashboard.
"""
import re
import speech_recognition as sr

SENSITIVE_KEYWORDS = [
    "chuyển khoản", "chuyen khoan", "số tài khoản", "so tai khoan", "stk",
    "ngân hàng", "chuyển gấp", "chuyển ngay", "50 triệu", "100 triệu",
    "đừng nói ai", "đừng báo ai", "bí mật", "mã otp", "wire transfer",
    "urgent transfer", "bank account", "confidential", "immediately",
]


def transcribe_audio(file_path: str, fallback_text: str = "") -> str:
    if fallback_text and fallback_text.strip():
        return fallback_text.strip()
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language="vi-VN")
    except Exception:
        return fallback_text or "Xin chào, đây là cuộc gọi kiểm tra hệ thống phòng thủ."


def analyze_intent(transcript: str):
    text_lower = transcript.lower()
    matched = [kw for kw in SENSITIVE_KEYWORDS if kw in text_lower]
    highlighted = transcript
    for kw in matched:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        highlighted = pattern.sub(lambda m: f"<mark class='kw-alert'>{m.group(0)}</mark>", highlighted)

    return {
        "sensitive": len(matched) > 0,
        "keywords": matched,
        "transcript": transcript,
        "highlighted_transcript": highlighted,
    }
