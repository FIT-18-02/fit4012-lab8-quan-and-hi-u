# Lab 8 - Threat Model

## 1. Mục tiêu bảo mật


Hệ thống trong Lab 8 được xây dựng nhằm đảm bảo:

- Bảo mật nội dung dữ liệu khi truyền qua mạng
- Bảo vệ khóa DES session key
- Phát hiện dữ liệu bị thay đổi
- Đảm bảo packet truyền đúng định dạng

Lab sử dụng mô hình Hybrid Encryption kết hợp:

- DES-CBC
- SHA-256
- RSA-OAEP

---

# 2. Tài sản cần bảo vệ

Các tài sản quan trọng trong hệ thống gồm:

| Tài sản | Ý nghĩa |
|---|---|
| Plaintext | Nội dung bản tin gốc cần được giữ bí mật |
| DES session key | Khóa đối xứng dùng để mã hóa plaintext |
| RSA private key của Receiver | Khóa bí mật dùng để giải mã DES key |
| Packet truyền qua socket | Dữ liệu truyền trên mạng cần tránh bị sửa đổi |
| Integrity của dữ liệu | Đảm bảo dữ liệu không bị thay đổi khi truyền |

---

# 3. Đối tượng tấn công giả định

Kẻ tấn công có khả năng:

- Nghe lén lưu lượng mạng
- Chặn packet trên đường truyền
- Sửa đổi packet
- Gửi packet giả mạo
- Replay lại packet cũ

Tuy nhiên giả định rằng:

- Kẻ tấn công không có RSA private key của Receiver
- Máy Receiver không bị chiếm quyền điều khiển
- Public key được phân phối đúng cho Sender

---

# 4. Các rủi ro chính

## 4.1 Nghe lén dữ liệu

Nếu dữ liệu được gửi dưới dạng plaintext, attacker có thể đọc toàn bộ nội dung.

### Giảm thiểu

- Sử dụng DES-CBC để mã hóa nội dung bản tin
- Plaintext không xuất hiện trực tiếp trên mạng

---

## 4.2 Lộ DES session key

Nếu DES key bị lộ, attacker có thể giải mã ciphertext.

### Giảm thiểu

- DES key được mã hóa bằng RSA-OAEP
- Chỉ Receiver có private key để giải mã DES key

---

## 4.3 Sửa đổi dữ liệu trên đường truyền

Attacker có thể thay đổi ciphertext hoặc packet.

### Giảm thiểu

- Sender tính SHA-256 hash của plaintext
- Receiver tính lại SHA-256 sau giải mã
- Nếu hash không khớp → phát hiện dữ liệu bị thay đổi

---

## 4.4 Packet sai định dạng

Packet bị cắt ngắn hoặc thêm dữ liệu thừa có thể gây lỗi parse.

### Giảm thiểu

- Packet sử dụng length header 4 byte
- Hàm parse kiểm tra:
  - độ dài encrypted key
  - độ dài ciphertext
  - SHA-256 digest size
  - dữ liệu dư thừa

---

# 5. Các hạn chế còn tồn tại

Mặc dù hệ thống hoạt động đúng yêu cầu Lab 8, vẫn còn nhiều hạn chế:

| Hạn chế | Giải thích |
|---|---|
| DES không còn an toàn | DES chỉ có effective key size nhỏ |
| Không xác thực Sender | Receiver chưa chứng minh được ai gửi dữ liệu |
| Không chống replay attack | Packet cũ có thể bị gửi lại |
| SHA-256 chưa phải authenticated encryption | Chỉ kiểm tra integrity sau giải mã |
| Chưa quản lý vòng đời khóa | Không có key rotation hoặc expiration |

---

# 6. Hướng cải tiến

Các hướng nâng cấp cho hệ thống:

## Thay DES bằng AES

- AES-128 hoặc AES-256 an toàn hơn DES
- IV dài 16 byte
- Hiệu quả và bảo mật tốt hơn

## Sử dụng AES-GCM

AES-GCM hỗ trợ:

- mã hóa dữ liệu
- xác thực integrity
- authenticated encryption

Giúp loại bỏ nhu cầu dùng hash rời rạc.

## Thêm chữ ký số

Sender có thể:

- ký dữ liệu bằng private key
- Receiver verify bằng public key

Giúp:

- xác thực danh tính Sender
- chống giả mạo dữ liệu

## Chống replay attack

Có thể thêm:

- nonce
- timestamp
- sequence number

để phát hiện packet cũ bị gửi lại.

---

# 7. Kết luận

Lab 8 giúp minh họa các thành phần quan trọng trong hệ thống truyền dữ liệu an toàn:

- DES-CBC bảo vệ nội dung
- SHA-256 kiểm tra integrity
- RSA-OAEP bảo vệ khóa đối xứng

Thông qua threat model, nhóm hiểu rõ hơn các nguy cơ bảo mật, giới hạn của DES và hướng phát triển sang các mô hình hiện đại hơn như AES-GCM và digital signature.
