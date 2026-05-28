import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import socket

import pytest
from Crypto.PublicKey import RSA

from secure_transfer_utils import (
    LENGTH_HEADER_SIZE,
    SHA256_DIGEST_SIZE,
    build_secure_packet,
    build_sender_payload,
    decrypt_des_cbc,
    decrypt_des_key_rsa,
    encrypt_des_cbc,
    encrypt_des_key_rsa,
    generate_des_key_iv,
    open_receiver_payload,
    pack_length,
    parse_length_header,
    parse_secure_packet,
    recv_exact,
    sha256_digest,
)


def test_des_cbc_roundtrip():
    plaintext = (
        "Xin chào FIT4012 - truyền dữ liệu an toàn"
        .encode("utf-8")
    )

    des_key, iv = generate_des_key_iv()

    _, _, ciphertext = encrypt_des_cbc(
        plaintext,
        des_key,
        iv,
    )

    assert ciphertext[:8] == iv

    decrypted = decrypt_des_cbc(
        des_key,
        ciphertext,
    )

    assert decrypted == plaintext


def test_des_rejects_wrong_key_size():
    with pytest.raises(ValueError):
        decrypt_des_cbc(
            b"short",
            b"12345678abcdefgh",
        )


def test_rsa_encrypt_decrypt_des_key():
    receiver_key = RSA.generate(2048)

    des_key, _ = generate_des_key_iv()

    encrypted = encrypt_des_key_rsa(
        des_key,
        receiver_key.publickey(),
    )

    decrypted = decrypt_des_key_rsa(
        encrypted,
        receiver_key,
    )

    assert encrypted != des_key

    assert decrypted == des_key


def test_full_sender_receiver_payload_success():
    receiver_key = RSA.generate(2048)

    plaintext = (
        b"Lab 8: DES-CBC + SHA-256 + RSA-OAEP"
    )

    packet, _, _, digest = build_sender_payload(
        plaintext,
        receiver_key.publickey(),
    )

    opened_plaintext, integrity_ok = (
        open_receiver_payload(
            packet,
            receiver_key,
        )
    )

    assert opened_plaintext == plaintext

    assert integrity_ok is True

    assert digest == sha256_digest(plaintext)


def test_tampered_hash_is_detected():
    receiver_key = RSA.generate(2048)

    packet, _, _, _ = build_sender_payload(
        b"original",
        receiver_key.publickey(),
    )

    tampered_packet = (
        packet[:-1]
        + bytes([packet[-1] ^ 0x01])
    )

    plaintext, integrity_ok = (
        open_receiver_payload(
            tampered_packet,
            receiver_key,
        )
    )

    assert plaintext == b"original"

    assert integrity_ok is False


def test_tampered_ciphertext_fails_or_changes_integrity():
    receiver_key = RSA.generate(2048)

    packet, _, _, _ = build_sender_payload(
        b"original message",
        receiver_key.publickey(),
    )

    mutable = bytearray(packet)

    mutable[-40] ^= 0x01

    try:
        plaintext, integrity_ok = (
            open_receiver_payload(
                bytes(mutable),
                receiver_key,
            )
        )

    except ValueError:
        return

    assert (
        plaintext != b"original message"
        or integrity_ok is False
    )


def test_length_header_roundtrip():
    data = b"hello"

    packed = pack_length(data)

    assert len(packed) == LENGTH_HEADER_SIZE

    parsed = parse_length_header(packed)

    assert parsed == len(data)


def test_build_and_parse_secure_packet():
    encrypted_key = b"A" * 256

    ciphertext = b"B" * 24

    digest = b"C" * SHA256_DIGEST_SIZE

    packet = build_secure_packet(
        encrypted_key,
        ciphertext,
        digest,
    )

    parsed_key, parsed_cipher, parsed_hash = (
        parse_secure_packet(packet)
    )

    assert parsed_key == encrypted_key

    assert parsed_cipher == ciphertext

    assert parsed_hash == digest


def test_parse_invalid_length_header():
    with pytest.raises(ValueError):
        parse_length_header(b"123")


def test_recv_exact_local_socket():
    server_sock, client_sock = socket.socketpair()

    try:
        client_sock.sendall(b"abcdefgh")

        data = recv_exact(server_sock, 8)

        assert data == b"abcdefgh"

    finally:
        server_sock.close()
        client_sock.close()


def test_pack_length_rejects_empty_data():
    with pytest.raises(ValueError):
        pack_length(b"")


def test_recv_exact_rejects_invalid_size():
    server_sock, client_sock = socket.socketpair()

    try:
        with pytest.raises(ValueError):
            recv_exact(server_sock, 0)

    finally:
        server_sock.close()
        client_sock.close()
