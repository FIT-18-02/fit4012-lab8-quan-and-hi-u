import os
import socket
from pathlib import Path


from secure_transfer_utils import (
    build_sender_payload,
    load_public_key,
    parse_secure_packet,
)

SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")

DATA_PORT = int(
    os.getenv("DATA_PORT", os.getenv("PORT", "6000"))
)

RECEIVER_PUBLIC_KEY = os.getenv(
    "RECEIVER_PUBLIC_KEY",
    "keys/receiver_public.pem",
)

MESSAGE_ENV = os.getenv("MESSAGE")

INPUT_FILE = os.getenv("INPUT_FILE", "")

LOG_FILE = os.getenv("SENDER_LOG_FILE", "")

TIMEOUT = float(
    os.getenv("SOCKET_TIMEOUT", "10")
)


def get_plaintext() -> bytes:
    """Read plaintext from file, env or keyboard."""

    if INPUT_FILE:
        input_path = Path(INPUT_FILE)

        if not input_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy file: {INPUT_FILE}"
            )

        data = input_path.read_bytes()

    elif MESSAGE_ENV is not None:
        data = MESSAGE_ENV.encode("utf-8")

    else:
        data = input("Nhập bản tin: ").encode("utf-8")

    if not data:
        raise ValueError("Plaintext không được rỗng.")

    return data


def send_packet(
    host: str,
    port: int,
    packet: bytes,
) -> None:
    """Connect and send one packet."""

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as sock:

        sock.settimeout(TIMEOUT)

        sock.connect((host, port))

        sock.sendall(packet)


def save_log(lines: list[str]) -> None:
    """Save sender log."""

    if not LOG_FILE:
        return

    log_path = Path(LOG_FILE)

    log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    lines = []

    try:
        plaintext = get_plaintext()

        receiver_public_key = load_public_key(
            RECEIVER_PUBLIC_KEY
        )

        (
            packet,
            des_key,
            ciphertext_with_iv,
            plaintext_hash,
        ) = build_sender_payload(
            plaintext,
            receiver_public_key,
        )

        encrypted_des_key, _, _ = parse_secure_packet(
            packet
        )

        send_packet(
            SERVER_IP,
            DATA_PORT,
            packet,
        )

        lines.extend([
            "[+] Đã tính SHA-256 của bản tin gốc.",
            "[+] Đã sinh DES key và IV ngẫu nhiên.",
            "[+] Đã mã hóa bản tin bằng DES-CBC.",
            "[+] Đã mã hóa DES key bằng RSA-OAEP.",
            "[+] Đã gửi packet an toàn qua socket.",
            f"Server IP: {SERVER_IP}",
            f"Port: {DATA_PORT}",
            f"Plaintext length: {len(plaintext)} bytes",
            f"DES key length: {len(des_key)} bytes",
            f"Encrypted DES key length: {len(encrypted_des_key)} bytes",
            f"Ciphertext length: {len(ciphertext_with_iv)} bytes",
            f"SHA-256: {plaintext_hash.hex()}",
        ])

        for line in lines:
            print(line)

    except Exception as error:
        error_message = f"[-] Sender error: {error}"

        lines.append(error_message)

        print(error_message)

    finally:
        save_log(lines)


if __name__ == "__main__":
    main()
