# ==============================================================================
# ORIGINAL REFERENCE CODE 2 (Dùng cho Mục 5.3 Báo cáo: Print out original code)
# Nguồn tham khảo (Reference Site):
#   - PyOTP Official Repository: https://github.com/pyauth/pyotp
#   - Librosa Official Docs: https://librosa.org/doc/latest/index.html
# Mô tả: Code gốc khởi tạo và kiểm tra mã xác thực một lần theo thời gian (TOTP)
#        chưa có máy trạng thái leo thang, chưa giới hạn số lần thử (Brute-force)
#        và chưa gắn với phiên cuộc gọi (call_id).
# ==============================================================================

import time
import pyotp

# 1. Sinh khóa bí mật Base32 ngẫu nhiên
secret = pyotp.random_base32()
print("Generated Secret:", secret)

# 2. Khởi tạo đối tượng TOTP (mặc định chu kỳ 30 giây)
totp = pyotp.TOTP(secret)

# 3. Sinh mã OTP 6 chữ số hiện tại
current_otp = totp.now()
print("Current OTP:", current_otp)

# 4. Kiểm tra mã OTP hợp lệ
is_valid = totp.verify(current_otp)
print("OTP Verified Immediately:", is_valid)
