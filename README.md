# 🛡️ Project 9: Deepfake Vishing Defense System with Visualization

Hệ thống phòng thủ đa kênh bảo vệ doanh nghiệp trước tấn công giả mạo giọng nói bằng AI (**Deepfake Vishing**) và lừa đảo chuyển khoản (**Social Engineering Wire-Transfer Fraud**).

---

## 🏗️ Cấu trúc Thư mục Dự án (Phân chia theo 3 thành viên A – B – C)

```text
├── ml/                         # [Thành viên A] Audio & Machine Learning (Librosa MFCC + SVM/RF)
│   ├── preprocess.py           # Chuẩn hóa âm thanh 16kHz mono & khởi tạo mẫu thử
│   ├── features.py             # Trích xuất 44 đặc trưng (MFCC, Spectral, ZCR) & vẽ Spectrogram
│   ├── train.py                # Huấn luyện, so sánh SVM vs Random Forest & tính EER
│   ├── detector.py             # Hàm chuẩn predict_audio() bàn giao cho Backend (Task A08)
│   └── test_robustness.py      # Kiểm thử độ bền nén điện thoại 8kHz (Task A07)
├── backend/                    # [Thành viên B] FastAPI, Intent Detection & Out-of-Band (PyOTP)
│   ├── oob_manager.py          # Sinh/Xác thực TOTP (PyOTP), TTL 60s & Chống Brute-Force (TC6)
│   ├── intent_detector.py      # Speech-to-Text & Quét từ khóa nhạy cảm Tiếng Việt/Anh
│   └── main.py                 # FastAPI Server (6 endpoints chuẩn Hợp đồng API + SQLite Log)
├── dashboard/                  # [Thành viên C] SOC Visualization Dashboard (4 màn hình)
│   └── index.html              # Giao diện trực quan hóa KPIs, Phổ âm thanh, OOB & Demo TC1..TC7
├── tests/                      # [Thành viên C] Kịch bản kiểm thử tự động (Task C08)
│   └── run_test_cases.py       # Chạy kiểm tra tự động toàn bộ 7 kịch bản TC1 -> TC7
├── reference_code/             # [Cả nhóm] Lưu Original Reference Code phục vụ Mục 5.3 Báo cáo
│   ├── ref_mfcc_original.py    # Code gốc trích xuất MFCC từ repo tham khảo
│   └── ref_pyotp_original.py   # Code mẫu gốc từ thư viện PyOTP
├── data/                       # Thư mục dữ liệu âm thanh (.wav)
│   ├── real/                   # Mẫu giọng thật (Bonafide)
│   ├── fake/                   # Mẫu giọng giả AI (Spoofed - tạo từ VieNeu-TTS / Dataset)
│   └── demo_cases/             # Các file kịch bản phục vụ Demo trực tiếp
├── requirements.txt            # Danh sách thư viện Python
└── run_demo.bat                # File chạy nhanh toàn bộ hệ thống trên Windows
```

---

## 🚀 Cách Chạy Hệ Thống Nhanh (Quick Start)

### 1. Kích hoạt môi trường ảo (Đã được cài đặt sẵn trong `.venv`)
```powershell
.\.venv\Scripts\activate
```

### 2. Huấn luyện mô hình phát hiện giọng giả (Thành viên A)
```powershell
python -m ml.train
```

### 3. Chạy kiểm tra tự động 7 Kịch bản Kiểm thử `TC1` $\rightarrow$ `TC7` (Thành viên C)
```powershell
python -m tests.run_test_cases
```

### 4. Khởi động Server & Mở Giao diện SOC Dashboard (Thành viên B & C)
```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
* Mở trình duyệt tại: **http://127.0.0.1:8000/** (Giao diện SOC Visualization Dashboard 4 màn hình).
* Tài liệu Swagger API tự động tại: **http://127.0.0.1:8000/docs**.
