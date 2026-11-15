"""
Module: backend/main.py (Phụ trách: Thành viên B - Task B01, B03, B06, B07)
Chức năng:
  - Cung cấp đầy đủ 6 REST API theo Hợp đồng API:
      1. POST /analyze-audio
      2. POST /detect-intent
      3. POST /otp/challenge
      4. POST /otp/verify
      5. POST /call-event
      6. GET  /events
  - Kèm endpoint chạy nhanh 7 kịch bản kiểm thử (POST /demo/run-tc) và phục vụ trực tiếp
    SOC Visualization Dashboard tại http://127.0.0.1:8000/
"""
import os
import json
import uuid
import shutil
import sqlite3
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ml.detector import predict_audio
from ml.preprocess import ensure_initial_dataset
from backend.intent_detector import transcribe_audio, analyze_intent
from backend.oob_manager import create_oob_challenge, verify_oob_challenge, CHALLENGES

app = FastAPI(title="Project 9: Deepfake Vishing Defense System API", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

os.makedirs("static/plots", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_PATH = "backend/events.db"
FAKE_THRESHOLD = float(os.getenv("FAKE_SCORE_THRESHOLD", "0.50"))


def init_db():
    os.makedirs("backend", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id TEXT,
                timestamp TEXT,
                fake_score REAL,
                label TEXT,
                transcript TEXT,
                highlighted_transcript TEXT,
                sensitive INTEGER,
                keywords TEXT,
                decision TEXT,
                risk_score REAL,
                challenge_id TEXT,
                oob_status TEXT,
                plot_url TEXT,
                features_json TEXT
            )"""
        )


init_db()
ensure_initial_dataset()


@app.get("/")
def serve_dashboard():
    return FileResponse("dashboard/index.html")


@app.post("/analyze-audio")
async def api_analyze_audio(audio: UploadFile = File(...)):
    call_id = f"AUD-{uuid.uuid4().hex[:5].upper()}"
    save_path = f"static/uploads/{call_id}_{audio.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)
    return predict_audio(save_path, call_id=call_id)


@app.post("/detect-intent")
async def api_detect_intent(
    transcript: str = Form(""), audio: UploadFile = File(None)
):
    text = transcript
    if not text and audio is not None:
        tmp_path = f"static/uploads/tmp_{audio.filename}"
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)
        text = transcribe_audio(tmp_path)
    return analyze_intent(text)


@app.post("/otp/challenge")
async def api_otp_challenge(call_id: str = Form("CALL-MANUAL")):
    return create_oob_challenge(call_id)


@app.post("/otp/verify")
async def api_otp_verify(
    challenge_id: str = Form(...),
    code: str = Form(...),
    force_expire: bool = Form(False),
):
    res = verify_oob_challenge(challenge_id, code, force_expire=force_expire)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE events SET decision=?, oob_status=? WHERE challenge_id=?",
            (res["decision"], res["status"], challenge_id),
        )
    return res


@app.get("/otp/active")
def api_otp_active():
    return list(CHALLENGES.values())


def _process_call_internal(file_path: str, call_id: str, transcript_hint: str):
    ml_res = predict_audio(file_path, call_id=call_id)
    fake_score = ml_res["fake_score"]

    raw_text = transcribe_audio(file_path, fallback_text=transcript_hint)
    intent_res = analyze_intent(raw_text)
    sensitive = intent_res["sensitive"]

    challenge_id, oob_status, expected_otp = "", "NONE", ""
    # Logic quyết định (All03):
    # 1. Yêu cầu nhạy cảm -> LUÔN kích hoạt thử thách OOB (nếu giọng giả rõ rệt thì vừa tạo OOB vừa đánh dấu rủi ro cực cao)
    # 2. Giọng giả (fake_score >= ngưỡng) dù yêu cầu thường -> ESCALATE
    # 3. Giọng thật + yêu cầu thường -> ALLOW
    if sensitive:
        ch = create_oob_challenge(call_id)
        challenge_id = ch["challenge_id"]
        oob_status = "PENDING"
        expected_otp = ch["expected_code"]
        decision = "challenge"
    elif fake_score >= FAKE_THRESHOLD:
        decision = "escalate"
    else:
        decision = "allow"

    risk_score = round(min(1.0, fake_score * 0.65 + (0.45 if sensitive else 0.0)), 2)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """INSERT INTO events (
                call_id, timestamp, fake_score, label, transcript,
                highlighted_transcript, sensitive, keywords, decision, risk_score,
                challenge_id, oob_status, plot_url, features_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                call_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                fake_score,
                ml_res["label"],
                intent_res["transcript"],
                intent_res["highlighted_transcript"],
                int(sensitive),
                json.dumps(intent_res["keywords"], ensure_ascii=False),
                decision,
                risk_score,
                challenge_id,
                oob_status,
                ml_res["plot_url"],
                json.dumps(ml_res["features_summary"], ensure_ascii=False),
            ),
        )

    return {
        "call_id": call_id,
        "decision": decision,
        "risk_score": risk_score,
        "fake_score": fake_score,
        "label": ml_res["label"],
        "sensitive": sensitive,
        "keywords": intent_res["keywords"],
        "transcript": intent_res["transcript"],
        "highlighted_transcript": intent_res["highlighted_transcript"],
        "challenge_id": challenge_id,
        "oob_status": oob_status,
        "expected_otp_demo": expected_otp,
        "plot_url": ml_res["plot_url"],
        "features_summary": ml_res["features_summary"],
    }


@app.post("/call-event")
async def api_call_event(
    call_id: str = Form(""),
    transcript_hint: str = Form(""),
    audio: UploadFile = File(...),
):
    cid = call_id.strip() or f"CALL-{uuid.uuid4().hex[:5].upper()}"
    save_path = f"static/uploads/{cid}_{audio.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)
    return _process_call_internal(save_path, cid, transcript_hint)


@app.post("/demo/run-tc")
async def api_run_test_case(tc_id: str = Form(...)):
    """Endpoint hỗ trợ chạy nhanh 7 kịch bản kiểm thử TC1 -> TC7 trên Dashboard."""
    ensure_initial_dataset()
    scenarios = {
        "TC1": (
            "data/demo_cases/tc1_real_normal.wav",
            "Chào phòng kế toán, chiều nay 14h mình họp giao ban tuần như bình thường nhé.",
        ),
        "TC2": (
            "data/demo_cases/tc2_fake_transfer.wav",
            "Alo em à, anh đang họp gấp, chuyển khoản ngay 50 triệu vào số tài khoản 1903888999 nhé, bí mật đừng nói ai!",
        ),
        "TC3": (
            "data/demo_cases/tc3_real_transfer.wav",
            "Em ơi, thực hiện lệnh chuyển khoản 100 triệu thanh toán hợp đồng vào số tài khoản đối tác giúp anh nhé.",
        ),
        "TC4": (
            "data/demo_cases/tc3_real_transfer.wav",
            "Em ơi, chuyển gấp 50 triệu vào số tài khoản ngân hàng này giúp anh nhé.",
        ),
        "TC5": (
            "data/demo_cases/tc3_real_transfer.wav",
            "Alo, chuyển khoản khẩn cấp cho đối tác trước 5 giờ chiều nay nhé.",
        ),
        "TC6": (
            "data/demo_cases/tc2_fake_transfer.wav",
            "Chuyển khoản gấp 100 triệu vào số tài khoản mới này, đừng báo ai!",
        ),
        "TC7": (
            "data/demo_cases/tc7_fake_normal.wav",
            "Alo, cho mình hỏi lịch làm việc của giám đốc tuần này như thế nào nhỉ?",
        ),
    }
    tc_key = tc_id.upper()
    wav_path, text = scenarios.get(tc_key, scenarios["TC1"])
    cid = f"{tc_key}-{uuid.uuid4().hex[:4].upper()}"
    res = _process_call_internal(wav_path, cid, text)

    # Tự động mô phỏng bước tiếp theo cho TC2, TC3, TC4, TC5, TC6 nếu cần
    if tc_key == "TC2" and res["challenge_id"]:
        v = verify_oob_challenge(res["challenge_id"], "000000")
        res["decision"] = v["decision"]
        res["oob_status"] = "FAILED_NO_DEVICE"
    elif tc_key == "TC3" and res["challenge_id"]:
        v = verify_oob_challenge(res["challenge_id"], res["expected_otp_demo"])
        res["decision"] = v["decision"]
        res["oob_status"] = v["status"]
    elif tc_key == "TC4" and res["challenge_id"]:
        v = verify_oob_challenge(res["challenge_id"], "999999")
        res["decision"] = v["decision"]
        res["oob_status"] = v["status"]
    elif tc_key == "TC5" and res["challenge_id"]:
        v = verify_oob_challenge(res["challenge_id"], res["expected_otp_demo"], force_expire=True)
        res["decision"] = v["decision"]
        res["oob_status"] = v["status"]
    elif tc_key == "TC6" and res["challenge_id"]:
        for _ in range(3):
            v = verify_oob_challenge(res["challenge_id"], "111111")
        res["decision"] = v["decision"]
        res["oob_status"] = v["status"]

    if res["challenge_id"]:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE events SET decision=?, oob_status=? WHERE challenge_id=?",
                (res["decision"], res["oob_status"], res["challenge_id"]),
            )
    return res


@app.get("/events")
def api_list_events():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT 50").fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["keywords"] = json.loads(d["keywords"] or "[]")
            d["features_summary"] = json.loads(d["features_json"] or "{}")
            out.append(d)
        return out
