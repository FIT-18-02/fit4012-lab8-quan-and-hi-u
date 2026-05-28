# Lab 8 - Báo cáo 1 trang


## 1. Mục tiêu

Mục tiêu của bài Lab 8 là xây dựng chương trình truyền dữ liệu an toàn giữa Sender và Receiver thông qua TCP socket bằng mô hình mã hóa lai (Hybrid Encryption).

Hệ thống sử dụng:

- DES-CBC để mã hóa nội dung bản tin
- SHA-256 để kiểm tra tính toàn vẹn dữ liệu
- RSA-OAEP để bảo vệ khóa DES khi truyền qua mạng

Thông qua bài lab, nhóm hiểu được cách phối hợp giữa mã hóa đối xứng, mã hóa bất đối xứng và cơ chế kiểm tra integrity trong hệ thống truyền dữ liệu an toàn.

---

# 2. Luồng xử lý Sender

Sender thực hiện các bước:

1. Đọc plaintext từ:
   - biến môi trường `MESSAGE`
   - file `INPUT_FILE`
   - hoặc nhập từ bàn phím

2. Tính SHA-256 hash của plaintext gốc để phục vụ kiểm tra integrity.

3. Sinh:
   - DES key 8 byte ngẫu nhiên
   - IV 8 byte ngẫu nhiên

4. Mã hóa plaintext bằng DES-CBC:
   - sử dụng PKCS#7 padding
   - ghép IV vào đầu ciphertext

5. Mã hóa DES key bằng RSA public key của Receiver thông qua RSA-OAEP.

6. Tạo packet theo format Lab 8:

```text
[len_key]
[encrypted_des_key]
[len_cipher]
[ciphertext]
[sha256_hash]
```

7. Gửi packet qua TCP socket đến Receiver.

---

# 3. Luồng xử lý Receiver

Receiver thực hiện các bước:

1. Lắng nghe kết nối TCP từ Sender.

2. Nhận packet và tách:
   - encrypted DES key
   - ciphertext
   - SHA-256 hash

3. Dùng RSA private key để giải mã DES key.

4. Tách IV khỏi ciphertext và giải mã dữ liệu bằng DES-CBC.

5. Tính lại SHA-256 của plaintext sau giải mã.

6. So sánh hash:
   - nếu khớp → dữ liệu nguyên vẹn
   - nếu không khớp → dữ liệu đã bị thay đổi hoặc giả mạo

7. Hiển thị plaintext sau khi giải mã và ghi log minh chứng.

---

# 4. Kết quả thực hiện

Hệ thống đã thực hiện thành công:

- Truyền dữ liệu giữa Sender và Receiver qua socket
- Mã hóa plaintext bằng DES-CBC
- Mã hóa DES key bằng RSA-OAEP
- Kiểm tra integrity bằng SHA-256
- Phát hiện dữ liệu bị thay đổi
- Lưu log quá trình gửi và nhận

Các file minh chứng:

- Log Sender:
  `logs/sender_success.log`

- Log Receiver:
  `logs/receiver_success.log`

- File input:
  `sample_input.txt`

- File output:
  `sample_output.txt`

---

# 5. Các test đã thực hiện

Nhóm đã viết test cho các trường hợp:

- DES encrypt/decrypt roundtrip
- RSA encrypt/decrypt DES key
- Packet format validation
- SHA-256 verification
- Modified hash detection
- Tampered ciphertext detection
- Invalid packet handling
- Socket helper local test

Tổng số test đáp ứng yêu cầu CI của Lab 8.

---

# 6. Nhận xét và đánh giá

RSA-OAEP giúp bảo vệ khóa DES khi truyền qua mạng, tránh việc gửi khóa đối xứng dưới dạng plaintext.

SHA-256 giúp Receiver phát hiện dữ liệu bị thay đổi sau khi truyền.

DES-CBC giúp che giấu nội dung bản tin, tuy nhiên DES hiện không còn đủ an toàn cho hệ thống thực tế do kích thước khóa nhỏ.

Hướng nâng cấp phù hợp hơn:

- AES-128 hoặc AES-256
- AES-GCM để vừa mã hóa vừa xác thực dữ liệu
- Digital Signature để xác minh danh tính Sender
- Chống replay attack bằng nonce hoặc timestamp

Thông qua bài lab, nhóm hiểu rõ hơn về cơ chế Hybrid Encryption và cách xây dựng hệ thống truyền dữ liệu an toàn cơ bản.****
