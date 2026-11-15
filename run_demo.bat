@echo off
echo ============================================================================
echo   PROJECT 9: DEEPFAKE VISHING DEFENSE SYSTEM WITH VISUALIZATION
echo ============================================================================
echo [1/3] Checking and training baseline model (ml/train.py)...
".\.venv\Scripts\python.exe" -m ml.train

echo [2/3] Opening SOC Dashboard at http://127.0.0.1:8000 ...
start "" "http://127.0.0.1:8000"

echo [3/3] Starting FastAPI Server on port 8000...
".\.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
