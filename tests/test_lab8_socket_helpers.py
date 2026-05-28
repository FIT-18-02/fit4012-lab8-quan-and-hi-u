import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import socket
import threading

from secure_transfer_utils import (
    SHA256_DIGEST_SIZE,
    build_secure_packet,
    recv_secure_packet,
)


def test_recv_secure_packet_over_local_socket():
    packet = build_secure_packet(
        b"k" * 256,
        b"c" * 24,
        b"h" * SHA256_DIGEST_SIZE,
    )

    left, right = socket.socketpair()

    def sender() -> None:
        with left:
            left.sendall(packet)

    thread = threading.Thread(
        target=sender,
        daemon=True,
    )

    thread.start()

    with right:
        received = recv_secure_packet(right)

    thread.join(timeout=2)

    assert received == packet
