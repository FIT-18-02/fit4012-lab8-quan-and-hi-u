[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/1tfxOnrV)
# FIT4012 - Lab 8 - Xây dựng ứng dụng truyền dữ liệu an toàn

## Team members


- Thành viên 1: Phạm Anh Quân - MSSV: 1871020471
- Thành viên 2: Ngô Văn Hiếu

## Task division

- Thành viên 1 phụ trách chính: Phạm Anh Quân
  - sender.py
  - DES-CBC encryption
  - tạo packet gửi qua socket
  - log phía Sender

- Thành viên 2 phụ trách chính: Ngô Văn Hiếu
  - receiver.py
  - RSA decrypt DES key
  - SHA-256 integrity verification
  - log phía Receiver

- Phần làm chung:cả 2
  - viết test
  - README
  - báo cáo
  - debug hệ thống socket

## Demo roles

- Demo Sender / mã hóa / log gửi: Hải Anh Quân
- Demo Receiver / giải mã / kiểm tra hash: Ngô Văn Hiếu
- Cả hai cùng trả lời câu hỏi mở rộng AES và chữ ký số

---

# Mục tiêu bài lab

Lab 8 xây dựng hệ thống truyền dữ liệu an toàn qua TCP socket bằng mô hình mã hóa lai:

- DES-CBC dùng để mã hóa nội dung bản tin
- SHA-256 dùng để kiểm tra tính toàn vẹn dữ liệu
- RSA-OAEP dùng để bảo vệ khóa DES khi truyền qua mạng

Hệ thống mô phỏng quá trình Sender gửi dữ liệu an toàn cho Receiver.

---

# Cấu trúc project

```text
.
├── secure_transfer_utils.py
├── keygen.py
├── sender.py
├── receiver.py
├── requirements.txt
├── sample_input.txt
├── sample_output.txt
├── report-1page.md
├── threat-model-1page.md
├── peer-review-response.md
├── logs/
├── keys/
├── tests/
└── .github/workflows/ci.yml
```

---

# Cài đặt môi trường

## Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

# Tạo khóa RSA

Chạy lệnh:

```bash
python keygen.py
```

Sau khi chạy sẽ tạo:

```text
keys/receiver_private.pem
keys/receiver_public.pem
```

- Receiver giữ private key
- Sender sử dụng public key để mã hóa DES key

---

# Protocol truyền dữ liệu

Packet được gửi theo định dạng:

```text
[len_key: 4 bytes]
[encrypted_des_key: N bytes]
[len_cipher: 4 bytes]
[ciphertext: M bytes]
[sha256_hash: 32 bytes]
```

Trong đó:

| Thành phần | Ý nghĩa |
|---|---|
| len_key | độ dài RSA encrypted DES key |
| encrypted_des_key | DES key được mã hóa bằng RSA-OAEP |
| len_cipher | độ dài ciphertext |
| ciphertext | IV + DES-CBC encrypted data |
| sha256_hash | SHA-256 của plaintext gốc |

---

# Chạy chương trình

## Terminal 1 - Receiver

```bash
RECEIVER_HOST=127.0.0.1 \
DATA_PORT=6000 \
RECEIVER_PRIVATE_KEY=keys/receiver_private.pem \
python receiver.py
```

## Terminal 2 - Sender

```bash
SERVER_IP=127.0.0.1 \
DATA_PORT=6000 \
RECEIVER_PUBLIC_KEY=keys/receiver_public.pem \
MESSAGE="Xin chao FIT4012 - Lab 8 Secure Transfer" \
python sender.py
```

---

# Chạy có log minh chứng

## Receiver

```bash
RECEIVER_HOST=127.0.0.1 \
DATA_PORT=6000 \
RECEIVER_PRIVATE_KEY=keys/receiver_private.pem \
RECEIVER_LOG_FILE=logs/receiver_success.log \
OUTPUT_FILE=sample_output.txt \
python receiver.py
```

## Sender

```bash
SERVER_IP=127.0.0.1 \
DATA_PORT=6000 \
RECEIVER_PUBLIC_KEY=keys/receiver_public.pem \
MESSAGE="Xin chao FIT4012 - Lab 8 Secure Transfer" \
SENDER_LOG_FILE=logs/sender_success.log \
python sender.py
```

---

# Gửi dữ liệu từ file

## Receiver

```bash
RECEIVER_HOST=127.0.0.1 DATA_PORT=6000 OUTPUT_FILE=sample_output.txt python receiver.py
```

## Sender

```bash
SERVER_IP=127.0.0.1 DATA_PORT=6000 INPUT_FILE=sample_input.txt python sender.py
```

---

# Chạy test

```bash
pytest -q
```

---

# Các chức năng đã thực hiện

- Mã hóa dữ liệu bằng DES-CBC
- Padding PKCS#7
- Sinh IV ngẫu nhiên
- Tính SHA-256 hash
- Kiểm tra integrity của dữ liệu
- RSA-OAEP encrypt/decrypt DES key
- TCP socket communication
- Packet format với length header
- Logging kết quả gửi/nhận
- Test các trường hợp lỗi

---

# Các test chính

Project có các test:

- DES encrypt/decrypt roundtrip
- RSA encrypt/decrypt DES key
- Packet format validation
- SHA-256 verification
- Tampered ciphertext detection
- Modified hash detection
- Socket helper test
- Invalid packet handling

---

# Câu hỏi mở rộng

## Q1. Thay DES bằng AES

- AES-128 sử dụng key 16 byte
- AES-256 sử dụng key 32 byte
- AES-CBC sử dụng IV 16 byte
- AES-GCM hỗ trợ vừa mã hóa vừa xác thực dữ liệu nên an toàn hơn CBC + hash rời rạc

## Q2. Thêm chữ ký số

Có thể mở rộng hệ thống bằng:

- Sender sử dụng private key để ký dữ liệu
- Receiver dùng public key của Sender để verify chữ ký
- Giúp xác minh danh tính Sender và chống giả mạo dữ liệu

---

# Threat model

Hệ thống giúp giảm các nguy cơ:

- Nghe lén dữ liệu trên mạng
- Lộ khóa DES khi truyền
- Chỉnh sửa nội dung packet
- Giả mạo ciphertext

Hạn chế:

- DES hiện không còn đủ mạnh cho hệ thống thực tế
- Chưa có xác thực danh tính Sender
- Chưa chống replay attack

---

# Ethics & Safe Use

- Chỉ sử dụng cho mục đích học tập
- Không triển khai trong hệ thống thật
- Không thử nghiệm trên hệ thống không được phép
- Không sử dụng dữ liệu nhạy cảm thật

---

# Kết luận

Lab 8 giúp hiểu cách kết hợp:

- DES-CBC để bảo mật nội dung
- SHA-256 để kiểm tra toàn vẹn
- RSA-OAEP để bảo vệ khóa đối xứng

Qua bài lab, nhóm hiểu được nguyên lý hoạt động của hybrid encryption trong hệ thống truyền dữ liệu an toàn.
