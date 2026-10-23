"""Quick checks for Phase  3 (RDT 3.0).

Usage (from the repo root):
    python scripts/test_rdt.py
"""
import hashlib
import os
import socket
import random
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from packet import TYPE_DATA, extract_packet, is_corrupt, make_ack, make_packet  # noqa: E402
from receiver import receive_file  # noqa: E402
from sender import send_file       # noqa: E402
from corruption import maybe_drop  # noqa: E402

FILE = os.path.join(ROOT, "data", "small.bmp")
OUT = os.path.join(ROOT, "results", "test_out.bmp")
NAMES = {1: "no errors", 2: "ACK bit-error", 3: "DATA bit-error",
         4: "ACK loss", 5: "DATA loss"}


def test_round_trip():
    pkt = make_packet(TYPE_DATA, 1, b"hello world")
    assert not is_corrupt(pkt)
    assert extract_packet(pkt) == (TYPE_DATA, 1, 0, b"hello world")
    assert not is_corrupt(make_ack(0))
    print("PASS packet round trip")


def test_every_single_bit_flip_is_caught():
    for pkt in (make_packet(TYPE_DATA, 0, os.urandom(1024)), make_ack(1)):
        for bit in range(len(pkt) * 8):
            bad = bytearray(pkt)
            bad[bit // 8] ^= 1 << (bit % 8)
            assert is_corrupt(bytes(bad)), f"missed flip at bit {bit}"
    print("PASS checksum catches every 1-bit error (DATA and ACK)")


def transfer(option, rate):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    t = threading.Thread(target=receive_file, kwargs=dict(
        out_path=OUT, option=option, error_rate=rate, quiet=True,
        sock=sock, linger=1.0))
    t.start()
    elapsed, stats = send_file(FILE, "127.0.0.1", sock.getsockname()[1], option, rate, quiet=True)
    t.join()
    same = hashlib.sha256(open(FILE, "rb").read()).digest() == \
        hashlib.sha256(open(OUT, "rb").read()).digest()
    assert same, f"option {option} ({NAMES[option]}) at {rate:.0%}: file does not match"
    print(f"PASS option {option} ({NAMES[option]}) at {rate:.0%}: file matches, "
          f"{stats.get('resent', '?')} resends, {elapsed:.2f} s")

def test_maybe_drop():
    rng = random.Random(42)
    assert not any(maybe_drop(0.0, rng) for _ in range(1000)), "rate 0 should never drop"
    assert all(maybe_drop(1.0, rng) for _ in range(1000)), "rate 1 should always drop"
    drops = sum(maybe_drop(0.3, rng) for _ in range(10000))
    assert 2700 < drops < 3300, f"rate 0.3 dropped {drops}/10000"
    print(f"PASS maybe_drop (0% -> 0, 100% -> all, 30% -> {drops / 100:.1f}%)")

if __name__ == "__main__":
    test_round_trip()
    test_every_single_bit_flip_is_caught()
    test_maybe_drop()
    transfer(1, 0.0)
    for opt in (2, 3, 4, 5):
        for rate in (0.3, 0.5):
            transfer(opt, rate)
    os.remove(OUT)
    print("ALL TESTS PASSED")
