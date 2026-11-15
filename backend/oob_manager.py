"""
Module: backend/oob_manager.py (Phụ trách: Thành viên B - Task B02 & B08)
Chức năng:
  - Tạo thử thách xác thực ngoài băng tần (Out-of-Band - OOB) bằng PyOTP (RFC 6238).
  - Giới hạn thời gian sống (TTL = 60s, kiểm thử TC5).
  - Giới hạn tối đa 3 lần nhập sai để chống tấn công đoán mã Brute-force (TC6).
  - Chống dùng lại mã cũ (Anti-Replay).
"""
import os
import time
import uuid
import pyotp

OTP_SECRET = os.getenv("VISHING_OTP_SECRET", "JBSWY3DPEHPK3PXP")
CHALLENGES = {}


def create_oob_challenge(call_id: str, ttl_seconds: int = 60, max_attempts: int = 3):
    totp = pyotp.TOTP(OTP_SECRET, interval=ttl_seconds)
    code = totp.now()
    challenge_id = f"CH-{uuid.uuid4().hex[:6].upper()}"
    now = time.time()
    CHALLENGES[challenge_id] = {
        "challenge_id": challenge_id,
        "call_id": call_id,
        "expected_code": code,
        "created_at": now,
        "expires_at": now + ttl_seconds,
        "attempts": 0,
        "max_attempts": max_attempts,
        "status": "PENDING",
    }
    return CHALLENGES[challenge_id]


def verify_oob_challenge(challenge_id: str, user_code: str, force_expire: bool = False):
    ch = CHALLENGES.get(challenge_id)
    if not ch:
        return {
            "verified": False,
            "status": "NOT_FOUND",
            "decision": "escalate",
            "reason": "Challenge ID không tồn tại",
        }

    if ch["status"] in ("VERIFIED", "LOCKED_BRUTEFORCE", "EXPIRED"):
        return {
            "verified": False,
            "status": ch["status"],
            "decision": "escalate",
            "reason": f"Chặn Replay: Thử thách đã ở trạng thái {ch['status']}",
        }

    if force_expire or time.time() > ch["expires_at"]:
        ch["status"] = "EXPIRED"
        return {
            "verified": False,
            "status": "EXPIRED",
            "decision": "escalate",
            "reason": "Mã OTP đã hết hạn (>60s) -> Tự động leo thang (TC5)",
        }

    ch["attempts"] += 1
    if str(user_code).strip() == ch["expected_code"]:
        ch["status"] = "VERIFIED"
        return {
            "verified": True,
            "status": "VERIFIED",
            "decision": "allow",
            "reason": "Xác thực OOB hợp lệ trên thiết bị thứ 2 (TC3)",
        }

    if ch["attempts"] >= ch["max_attempts"]:
        ch["status"] = "LOCKED_BRUTEFORCE"
        return {
            "verified": False,
            "status": "LOCKED_BRUTEFORCE",
            "decision": "escalate",
            "reason": "Nhập sai quá 3 lần -> Khóa thử thách chống Brute-Force & Báo động (TC6)",
        }

    ch["status"] = "FAILED_ATTEMPT"
    return {
        "verified": False,
        "status": "FAILED_ATTEMPT",
        "remaining_attempts": ch["max_attempts"] - ch["attempts"],
        "decision": "escalate",
        "reason": f"Mã OTP sai ({ch['attempts']}/{ch['max_attempts']} lần) -> Cảnh báo leo thang (TC4)",
    }
