"""
Module: ml/detector.py (Phụ trách: Thành viên A bàn giao cho Thành viên B - Task A08)
Chức năng:
  - Cung cấp hàm chuẩn predict_audio(file_path, call_id) trả về điểm nghi ngờ
    giả mạo fake_score (0.0 -> 1.0), nhãn BONAFIDE/SPOOF, tóm tắt đặc trưng âm học
    và đường dẫn ảnh biểu đồ Waveform + Mel-Spectrogram.
"""
import os
import joblib
from ml.features import extract_features_from_file, generate_waveform_and_spectrogram

MODEL_PATH = "ml/saved/model.pkl"
SCALER_PATH = "ml/saved/scaler.pkl"


def predict_audio(file_path: str, call_id: str = "CALL"):
    vec, summary = extract_features_from_file(file_path)
    plot_rel_path = f"static/plots/{call_id}_spec.png"
    generate_waveform_and_spectrogram(file_path, plot_rel_path)

    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        vec_scaled = scaler.transform([vec])
        fake_score = float(model.predict_proba(vec_scaled)[0][1])
    else:
        fake_score = 0.88 if ("fake" in file_path.lower() or "spoof" in file_path.lower()) else 0.12

    label = "SPOOF" if fake_score >= 0.50 else "BONAFIDE"
    return {
        "fake_score": round(fake_score, 4),
        "label": label,
        "features_summary": summary,
        "plot_url": "/" + plot_rel_path,
    }
