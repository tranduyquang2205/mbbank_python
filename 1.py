import hashlib
import time

import hashlib
import time
import requests

# Thông số từ API trả về
nonce = "1ea6a1cdcaa72da0fca7"
difficulty_bits = 20  # 20 bits = 5 hex 0s
token = "AAQAAAAL_____287uRN5SyCtipj-dw50W1wdaluG__m6N4NrZhnZPONtuZB_NqGjYR6a7yAHXVTG__3ZE7gd3RDsWso_c0gEpSg2TnY4r55IU4dSNcngPt4chGuDpYAZDPCCkM119rMIl5UGIQA4GQQWASrCEcy0TxF31az_Q7XyKuSoggK2EJQo94qBzeyC6zzMD_kZnQ-cYm88KlUYyjOU222hJLoqHvvNNwSiHbMDa1ymW0F0fUnYLvQMB3_itQjvJP0yUuYxdGryM9lp9aMM7eDIOobDK8AweHw_7Di3SN617K4dbdFwjvEH-OgbQ_78L5cklFcjVDFK5Xvvzos0N1Nc1g"
timestamp = 1743760115
verify_url = "https://online.mbbank.com.vn/Qme_wRXAq/Z/bVfaWYAQ/hG7Gpkhu5bu9/SVxmbzkhJAE/NS0lfUs/1Vwg"

# Hàm giải challenge
def solve_pow(nonce, bits):
    prefix = "0" * (bits // 4)
    for i in range(10000000):
        data = f"{nonce}{i}".encode()
        hash_result = hashlib.sha256(data).hexdigest()
        if hash_result.startswith(prefix):
            return i
    return None

solution = solve_pow(nonce, difficulty_bits)
print("Found solution:", solution)


# Giờ bạn có thể dùng solution này để gọi verify_url kèm theo token, nonce, timestamp, solution...
# Gửi request xác minh (có thể là GET hoặc POST, tùy API)
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0',  # giả lập browser nếu cần
}

payload = {
    "token": token,
    "nonce": nonce,
    "timestamp": timestamp,
    "solution": solution
}

# Gửi request
response = requests.post(verify_url, json=payload, headers=headers, verify=False)

print("Response status:", response.status_code)
print("Response body:", response.text)
