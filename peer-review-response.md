# Lab 8 - Peer Review Response

## Thông tin nhóm được review


- Tên nhóm: Phạm Anh Quân và Ngô Văn Hiếu
- Người review: Phạm Anh Quân
- Ngày review: 28/05/2026

---

## Nội dung góp ý nhận được

1. README còn thiếu mô tả chi tiết về protocol truyền dữ liệu.
2. Chưa có kiểm tra lỗi khi ciphertext bị thay đổi.
3. Thiếu test cho packet format và hash verification.
4. Cần bổ sung log minh chứng khi Sender và Receiver chạy thành công.
5. Nên mô tả rõ hơn vai trò của RSA-OAEP trong hệ thống.

---

## Phản hồi và chỉnh sửa của nhóm

| Góp ý | Phản hồi của nhóm | File/commit đã sửa |
|---|---|---|
| README còn thiếu mô tả protocol truyền dữ liệu | Đã bổ sung packet structure, giải thích từng trường dữ liệu và luồng truyền dữ liệu giữa Sender và Receiver | README.md |
| Chưa có kiểm tra lỗi khi ciphertext bị thay đổi | Đã bổ sung xử lý phát hiện dữ liệu bị can thiệp thông qua SHA-256 verification | receiver.py |
| Thiếu test cho packet format và hash verification | Đã bổ sung test packet parser, hash mismatch và tampered ciphertext | tests/test_protocol.py |
| Cần bổ sung log minh chứng khi Sender và Receiver chạy thành công | Đã bổ sung thư mục logs và lưu log cho cả Sender và Receiver | logs/, sender.py, receiver.py |
| Nên mô tả rõ hơn vai trò của RSA-OAEP trong hệ thống | Đã cập nhật README và report giải thích RSA-OAEP dùng để bảo vệ DES key khi truyền qua mạng | README.md, report-1page.md |

---

## Các cải tiến sau peer review

Sau khi nhận góp ý, nhóm đã cải thiện:

- Hoàn thiện README đầy đủ hơn
- Bổ sung kiểm tra integrity bằng SHA-256
- Tăng số lượng test cho các trường hợp lỗi
- Hoàn thiện logging cho demo
- Kiểm tra packet length và dữ liệu nhận qua socket
- Tổ chức lại cấu trúc project rõ ràng hơn
- Đảm bảo GitHub Actions và pytest chạy thành công

---

## Tự đánh giá sau chỉnh sửa

| Nội dung | Kết quả |
|---|---|
| Chương trình Sender/Receiver hoạt động | YES |
| Có mã hóa DES-CBC | YES |
| Có SHA-256 integrity check | YES |
| Có RSA-OAEP encrypt/decrypt DES key | YES |
| Có packet format đúng yêu cầu Lab 8 | YES |
| Có test tampered ciphertext | YES |
| Có test modified hash | YES |
| Có test DES roundtrip | YES |
| Có log minh chứng | YES |
| Có sample input/output | YES |
| GitHub Actions CI pass | YES |

---

## Kết luận

Sau quá trình peer review và chỉnh sửa, nhóm đã hoàn thiện hệ thống truyền dữ liệu an toàn theo đúng yêu cầu của Lab 8:

- DES-CBC dùng để mã hóa nội dung
- SHA-256 dùng để kiểm tra toàn vẹn dữ liệu
- RSA-OAEP dùng để bảo vệ khóa DES
- TCP socket dùng để truyền dữ liệu giữa Sender và Receiver

Nhóm hiểu được nguyên lý hoạt động của hybrid encryption và các thành phần cần thiết trong một hệ thống truyền dữ liệu an toàn cơ bản.
