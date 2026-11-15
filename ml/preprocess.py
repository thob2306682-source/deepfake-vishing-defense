"""
Module: ml/preprocess.py (Phụ trách: Thành viên A - Task A02 & A03)
Chức năng:
  - Tạo sẵn bộ dữ liệu âm thanh mẫu (data/real, data/fake, data/demo_cases)
    nếu thư mục đang trống để cả nhóm có thể chạy kiểm thử ngay từ Tuần 1.
  - Chuẩn hóa sample rate 16kHz mono cho các file âm thanh thực tế.
"""
import os
import numpy as np
import soundfile as sf

SAMPLE_RATE = 16000


def synthesize_voice_like_signal(duration=2.8, is_fake=False, seed=0):
    """
    Sinh tín hiệu âm thanh mô phỏng đặc trưng giọng thật (có biến thiên tự nhiên,
    hài âm phong phú) vs giọng tổng hợp AI (quá mượt ở tần số cao, thiếu vi biến thiên).
    Dùng làm dữ liệu khởi tạo ban đầu trước khi tải tập lớn từ Hugging Face / VieNeu-TTS.
    """
    rng = np.random.default_rng(seed)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

    f0 = rng.uniform(115, 210)
    if is_fake:
        # Giọng tổng hợp: tần số cơ bản đều đặn nhân tạo, hài âm bậc cao bị suy giảm đột ngột
        vibrato = 0.5 * np.sin(2 * np.pi * 5.0 * t)
        signal = (
            0.55 * np.sin(2 * np.pi * (f0 + vibrato) * t)
            + 0.25 * np.sin(2 * np.pi * 2 * f0 * t)
            + 0.08 * np.sin(2 * np.pi * 3 * f0 * t)
            + 0.008 * rng.normal(0, 1, len(t))
        )
        # Hiệu ứng cắt dải tần và lượng tử hóa của codec tổng hợp
        signal = np.round(signal * 32) / 32
    else:
        # Giọng thật: có jitter/shimmer tự nhiên, hài âm dải rộng và nhiễu môi trường tự nhiên
        jitter = np.cumsum(rng.normal(0, 0.35, len(t)))
        signal = (
            0.45 * np.sin(2 * np.pi * f0 * t + jitter * 0.05)
            + 0.22 * np.sin(2 * np.pi * 2 * f0 * t + 0.3)
            + 0.14 * np.sin(2 * np.pi * 3 * f0 * t + 0.7)
            + 0.09 * np.sin(2 * np.pi * 5 * f0 * t)
            + 0.06 * np.sin(2 * np.pi * 8 * f0 * t)
            + 0.045 * rng.normal(0, 1, len(t))
        )

    envelope = np.ones_like(t)
    fade = int(0.08 * SAMPLE_RATE)
    envelope[:fade] = np.linspace(0, 1, fade)
    envelope[-fade:] = np.linspace(1, 0, fade)
    signal = signal * envelope
    signal = signal / (np.max(np.abs(signal)) + 1e-6) * 0.85
    return signal.astype(np.float32)


def ensure_initial_dataset():
    """Tạo 40 file mẫu trong data/real, data/fake và 4 file kịch bản trong data/demo_cases."""
    os.makedirs("data/real", exist_ok=True)
    os.makedirs("data/fake", exist_ok=True)
    os.makedirs("data/demo_cases", exist_ok=True)

    for i in range(1, 21):
        r_path = f"data/real/sample_real_{i:02d}.wav"
        f_path = f"data/fake/sample_fake_{i:02d}.wav"
        if not os.path.exists(r_path):
            sf.write(r_path, synthesize_voice_like_signal(is_fake=False, seed=100 + i), SAMPLE_RATE)
        if not os.path.exists(f_path):
            sf.write(f_path, synthesize_voice_like_signal(is_fake=True, seed=200 + i), SAMPLE_RATE)

    demo_files = {
        "data/demo_cases/tc1_real_normal.wav": (False, 301),
        "data/demo_cases/tc2_fake_transfer.wav": (True, 302),
        "data/demo_cases/tc3_real_transfer.wav": (False, 303),
        "data/demo_cases/tc7_fake_normal.wav": (True, 307),
    }
    for path, (is_fake, seed) in demo_files.items():
        if not os.path.exists(path):
            sf.write(path, synthesize_voice_like_signal(duration=3.0, is_fake=is_fake, seed=seed), SAMPLE_RATE)

    print("[Preprocess] Đã khởi tạo đầy đủ file âm thanh mẫu trong data/real, data/fake và data/demo_cases.")


if __name__ == "__main__":
    ensure_initial_dataset()
