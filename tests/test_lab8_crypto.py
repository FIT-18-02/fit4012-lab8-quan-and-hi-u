import struct
from Crypto.Cipher import DES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

# Định nghĩa các hằng số cấu trúc dựa trên test suite
LENGTH_HEADER_SIZE = 4       # Dùng 4 bytes (với định dạng '!I') để lưu độ dài dữ liệu
SHA256_DIGEST_SIZE = 32      # SHA-256 luôn cho ra mã hash 32 bytes
RSA_KEY_SIZE_BYTES = 256     # RSA-2048 cho ra kết quả mã hóa ciphertext dài 256 bytes

def generate_des_key_iv():
    """Tạo khóa DES (8 bytes) và vector khởi tạo IV (8 bytes)."""
    des_key = get_random_bytes(8)
    iv = get_random_bytes(8)
    return des_key, iv

def encrypt_des_cbc(plaintext, des_key, iv):
    """Mã hóa DES-CBC với PKCS7 padding. Trả về iv, padding_len, và ciphertext (gắn kèm IV ở đầu)."""
    if len(des_key) != 8:
        raise ValueError("Khóa DES phải dài đúng 8 bytes.")
    
    cipher = DES.new(des_key, DES.MODE_CBC, iv)
    padded_data = pad(plaintext, DES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    
    # Ca test `test_des_cbc_roundtrip` yêu cầu `ciphertext[:8] == iv`
    final_ciphertext = iv + ciphertext
    return iv, len(padded_data) - len(plaintext), final_ciphertext

def decrypt_des_cbc(des_key, ciphertext):
    """Giải mã DES-CBC, bóc tách IV từ đầu chuỗi ciphertext và gỡ padding."""
    if len(des_key) != 8:
        raise ValueError("Khóa DES phải dài đúng 8 bytes.")
        
    iv = ciphertext[:8]
    actual_ciphertext = ciphertext[8:]
    
    cipher = DES.new(des_key, DES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(actual_ciphertext)
    return unpad(decrypted_padded, DES.block_size)

def encrypt_des_key_rsa(des_key, rsa_public_key):
    """Mã hóa khóa DES bằng khóa RSA Public sử dụng PKCS1_OAEP."""
    cipher = PKCS1_OAEP.new(rsa_public_key)
    return cipher.encrypt(des_key)

def decrypt_des_key_rsa(encrypted_key, rsa_private_key):
    """Giải mã khóa DES bằng khóa RSA Private."""
    cipher = PKCS1_OAEP.new(rsa_private_key)
    return cipher.decrypt(encrypted_key)

def sha256_digest(data):
    """Tính toán mã băm SHA-256 của dữ liệu đầu vào."""
    h = SHA256.new()
    h.update(data)
    return h.digest()

def pack_length(data):
    """Đóng gói độ dài của chuỗi bytes thành 4 bytes dạng Big-endian. Không nhận chuỗi rỗng."""
    if not data:
        raise ValueError("Dữ liệu trống không hợp lệ.")
    return struct.pack('!I', len(data))

def parse_length_header(header_bytes):
    """Giải nén 4 bytes header để lấy độ dài (integer)."""
    if len(header_bytes) != LENGTH_HEADER_SIZE:
        raise ValueError(f"Độ dài header phải đúng {LENGTH_HEADER_SIZE} bytes.")
    return struct.unpack('!I', header_bytes)[0]

def build_secure_packet(encrypted_key, ciphertext, digest):
    """Ghép nối tuần tự các phần dữ liệu thành một gói tin bảo mật hoàn chỉnh."""
    return encrypted_key + ciphertext + digest

def parse_secure_packet(packet):
    """Bóc tách gói tin dựa trên kích thước cố định của RSA Key (256 bytes) và SHA-256 (32 bytes)."""
    encrypted_key = packet[:RSA_KEY_SIZE_BYTES]
    digest = packet[-SHA256_DIGEST_SIZE:]
    ciphertext = packet[RSA_KEY_SIZE_BYTES:-SHA256_DIGEST_SIZE]
    return encrypted_key, ciphertext, digest

def build_sender_payload(plaintext, rsa_public_key):
    """Phía gửi: Mã hóa dữ liệu, băm dữ liệu, mã hóa khóa và đóng gói toàn bộ."""
    digest = sha256_digest(plaintext)
    des_key, iv = generate_des_key_iv()
    
    _, _, ciphertext = encrypt_des_cbc(plaintext, des_key, iv)
    encrypted_key = encrypt_des_key_rsa(des_key, rsa_public_key)
    
    packet = build_secure_packet(encrypted_key, ciphertext, digest)
    return packet, encrypted_key, ciphertext, digest

def open_receiver_payload(packet, rsa_private_key):
    """Phía nhận: Gỡ gói tin, giải mã khóa, giải mã dữ liệu và kiểm tra tính toàn vẹn (Integrity)."""
    encrypted_key, ciphertext, received_digest = parse_secure_packet(packet)
    
    try:
        des_key = decrypt_des_key_rsa(encrypted_key, rsa_private_key)
        plaintext = decrypt_des_cbc(des_key, ciphertext)
    except (ValueError, TypeError):
        # Trả về lỗi định dạng hoặc lỗi giải mã nếu gói tin bị can thiệp quá sâu vào cấu trúc
        raise ValueError("Gói tin bị lỗi cấu trúc dữ liệu hoặc sai khóa.")
        
    actual_digest = sha256_digest(plaintext)
    integrity_ok = (actual_digest == received_digest)
    
    return plaintext, integrity_ok

def recv_exact(sock, size):
    """Nhận chính xác số lượng `size` bytes từ một socket. Ném lỗi nếu size <= 0."""
    if size <= 0:
        raise ValueError("Kích thước nhận phải lớn hơn 0.")
    
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            break
        data += packet
    return data
