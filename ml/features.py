"""
Module: ml/features.py (Phụ trách: Thành viên A - Task A04)
Chức năng:
  1. Trích xuất 44 đặc trưng âm thanh bằng Librosa (20 MFCC mean + 20 MFCC std +
     Spectral Centroid + Spectral Rolloff + Zero-Crossing Rate + RMS Energy).
  2. Vẽ biểu đồ Sóng âm (Waveform) & Phổ Mel-Spectrogram phục vụ trực quan hóa
     trên SOC Dashboard của Thành viên C.
"""
import os
import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SAMPLE_RATE = 16000
N_MFCC = 20


def extract_features_from_file(file_path: str):
    """Trích xuất vector 44 đặc trưng và dictionary tóm tắt chỉ số âm học."""
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
    y_trimmed, _ = librosa.effects.trim(y, top_db=25)
    if len(y_trimmed) < int(sr * 0.25):
        y_trimmed = y

    mfcc = librosa.feature.mfcc(y=y_trimmed, sr=sr, n_mfcc=N_MFCC)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y_trimmed, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y_trimmed, sr=sr)))
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=y_trimmed)))
    rms = float(np.mean(librosa.feature.rms(y=y_trimmed)))

    feature_vector = np.concatenate([mfcc_mean, mfcc_std, [centroid, rolloff, zcr, rms]])
    summary = {
        "mfcc_1_mean": round(float(mfcc_mean[0]), 2),
        "spectral_centroid_hz": round(centroid, 1),
        "spectral_rolloff_hz": round(rolloff, 1),
        "zero_crossing_rate": round(zcr, 4),
        "rms_energy": round(rms, 4),
        "duration_sec": round(len(y) / sr, 2),
    }
    return feature_vector, summary


def generate_waveform_and_spectrogram(file_path: str, out_png_path: str):
    """Xuất ảnh ghép Waveform + Mel-Spectrogram hiển thị trên Dashboard."""
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.2), dpi=140)

    librosa.display.waveshow(y, sr=sr, ax=axes[0], color="#1F3864")
    axes[0].set_title("Waveform (Biên độ theo thời gian)", fontsize=10, fontweight="bold")
    axes[0].set_xlabel("Thời gian (s)")
    axes[0].set_ylabel("Biên độ")

    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    img = librosa.display.specshow(
        S_dB, x_axis="time", y_axis="mel", sr=sr, fmax=8000, ax=axes[1], cmap="magma"
    )
    axes[1].set_title("Mel-Spectrogram (Phổ tần số phát hiện giọng AI)", fontsize=10, fontweight="bold")
    fig.colorbar(img, ax=axes[1], format="%+2.0f dB")

    os.makedirs(os.path.dirname(out_png_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_png_path, bbox_inches="tight")
    plt.close(fig)
    return out_png_path
