"""
Module: ml/test_robustness.py (Phụ trách: Thành viên A - Task A07)
Chức năng:
  - Đánh giá độ bền của mô hình phát hiện giọng giả khi âm thanh bị nén qua kênh
    điện thoại (downsample xuống 8 kHz và thêm nhiễu nền).
  - Xuất số liệu phục vụ Mục 5.6 và Mục 6.1/6.2 trong Báo cáo.
"""
import glob
import os
import tempfile
import librosa
import numpy as np
import soundfile as sf
from ml.detector import predict_audio


def evaluate_phone_compression_robustness():
    fake_files = sorted(glob.glob("data/fake/*.wav"))[:10]
    clean_detected, compressed_detected = 0, 0

    for f in fake_files:
        res_clean = predict_audio(f, call_id="clean_test")
        if res_clean["label"] == "SPOOF":
            clean_detected += 1

        # Mô phỏng nén kênh điện thoại 8kHz + nhiễu đường truyền
        y, sr = librosa.load(f, sr=16000, mono=True)
        y_8k = librosa.resample(y, orig_sr=16000, target_sr=8000)
        y_back = librosa.resample(y_8k, orig_sr=8000, target_sr=16000)
        rng = np.random.default_rng(42)
        y_noisy = y_back + 0.03 * rng.normal(0, 1, len(y_back))

        tmp_wav = os.path.join(tempfile.gettempdir(), "degraded_8k.wav")
        sf.write(tmp_wav, y_noisy, 16000)
        res_deg = predict_audio(tmp_wav, call_id="deg_test")
        if res_deg["label"] == "SPOOF":
            compressed_detected += 1

    total = len(fake_files)
    print(f"[Robustness A07] Âm thanh gốc 16kHz: Phát hiện {clean_detected}/{total} mẫu giả.")
    print(f"[Robustness A07] Âm thanh nén điện thoại 8kHz + nhiễu: Phát hiện {compressed_detected}/{total} mẫu giả.")


if __name__ == "__main__":
    evaluate_phone_compression_robustness()
