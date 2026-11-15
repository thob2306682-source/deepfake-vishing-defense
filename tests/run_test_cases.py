"""
Module: tests/run_test_cases.py (Phụ trách: Thành viên C - Task C08)
Chức năng:
  - Tự động chạy toàn bộ 7 kịch bản kiểm thử (TC1 -> TC7) trực tiếp trên FastAPI
    và in bảng đối chiếu Kết quả mong đợi vs Kết quả thực tế.
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

EXPECTED = {
    "TC1": ("allow", "Giọng thật + Yêu cầu thường -> Cho phép (allow)"),
    "TC2": ("escalate", "Giọng giả + Chuyển khoản + Không có OOB -> Báo động (escalate)"),
    "TC3": ("allow", "Giọng thật + Chuyển khoản + OOB Đúng -> Cho phép (allow)"),
    "TC4": ("escalate", "Giọng thật + Chuyển khoản + OOB Sai mã -> Báo động (escalate)"),
    "TC5": ("escalate", "OTP hết hạn (>60s) -> Báo động (escalate)"),
    "TC6": ("escalate", "Nhập sai OTP 3 lần (Brute-force) -> Khóa & Báo động (escalate)"),
    "TC7": ("escalate", "Giọng giả + Yêu cầu thường -> Bắt bởi MFCC Detector (escalate)"),
}


def run_all_tests():
    print("\n" + "=" * 88)
    print("BẢNG KẾT QUẢ CHẠY 7 KỊCH BẢN KIỂM THỬ (TASK C08 - DÙNG CHO SHEET 'TEST CASES' & MỤC 5.5)")
    print("=" * 88)
    passed = 0
    for tc_id, (exp_decision, desc) in EXPECTED.items():
        resp = client.post("/demo/run-tc", data={"tc_id": tc_id})
        data = resp.json()
        actual = data["decision"]
        ok = actual == exp_decision
        if ok:
            passed += 1
        status_str = "ĐẠT (PASS)" if ok else "KHÔNG ĐẠT (FAIL)"
        print(
            f"[{tc_id}] {desc:62s} | Thực tế: {actual:8s} | OOB: {data['oob_status']:17s} | {status_str}"
        )
    print("=" * 88)
    print(f"=> TỔNG KẾT: Đạt {passed}/{len(EXPECTED)} kịch bản kiểm thử.\n")


if __name__ == "__main__":
    run_all_tests()
