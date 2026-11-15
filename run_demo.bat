@echo off
chcp 65001 >nul
echo ============================================================================
echo   PROJECT 9: DEEPFAKE VISHING DEFENSE SYSTEM WITH VISUALIZATION
echo ============================================================================
echo [1/3] Đang kiểm tra & huấn luyện mô hình cơ bản (ml/train.py)...
.\.venv\Scripts\python.exe -m ml.train

echo [2/3] Đang mở trình duyệt tại http://127.0.0.1:8000 ...
start http://127.0.0.1:8000

echo [3/3] Đang khởi động FastAPI Server tại cổng 8000...
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
