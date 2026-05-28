import os
import socket
from pathlib import Path

from secure_transfer_utils import (
    load_private_key,
    open_receiver_payload,
    recv_secure_packet,
)


HOST = os.getenv("RECEIVER_HOST", "0.0.0.0")
DATA_PORT = int(os.getenv("DATA_PORT", os.getenv("PORT", "6000")))
RECEIVER_PRIVATE_KEY = os.getenv(
    "RECEIVER_PRIVATE_KEY",
    "keys/receiver_private.pem",
)

TIMEOUT = float(os.getenv("SOCKET_TIMEOUT", "10"))

OUTPUT_FILE = os.getenv("OUTPUT_FILE", "")
LOG_FILE = os.getenv("RECEIVER_LOG_FILE", "")


def receive_packet() -> bytes:
    """Listen for one sender connection and receive one secure packet."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind((HOST, DATA_PORT))
        server.listen(1)

        print(f"[*] Receiver đang lắng nghe tại {HOST}:{DATA_PORT}")

        conn, addr = server.accept()

        with conn:
            conn.settimeout(TIMEOUT)

            print(f"[+] Đã nhận kết nối từ {addr[0]}:{addr[1]}")

            packet = recv_secure_packet(conn)

            return packet


def save_log(lines: list[str]) -> None:
    """Save receiver log file."""

    if not LOG_FILE:
        return

    log_path = Path(LOG_FILE)

    log_path.parent.mkdir(parents=True, exist_ok=True)

    log_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def save_output(data: bytes) -> None:
    """Save decrypted output file."""

    if not OUTPUT_FILE:
        return

    output_path = Path(OUTPUT_FILE)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_bytes(data)


def main() -> None:
    lines = []

    try:
        packet = receive_packet()

        receiver_private_key = load_private_key(
            RECEIVER_PRIVATE_KEY
        )

        plaintext, integrity_ok = open_receiver_payload(
            packet,
            receiver_private_key,
        )

        message = plaintext.decode(
            "utf-8",
            errors="replace",
        )

        if integrity_ok:
            lines.append(
                "[+] Dữ liệu nguyên vẹn: SHA-256 khớp."
            )
        else:
            lines.append(
                "[-] Dữ liệu bị thay đổi hoặc giả mạo: SHA-256 không khớp."
            )

        lines.extend([
            "[+] Đã giải mã DES key bằng RSA private key.",
            "[+] Đã giải mã ciphertext bằng DES-CBC.",
            f"[+] Bản tin gốc: {message}",
        ])

        for line in lines:
            print(line)

        save_output(plaintext)

    except Exception as error:
        error_message = f"[-] Receiver error: {error}"

        lines.append(error_message)

        print(error_message)

    finally:
        save_log(lines)


if __name__ == "__main__":
    main()
