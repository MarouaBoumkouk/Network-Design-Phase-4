"""Bit-error injection used by Option 2 (ACKs) and Option 3 (DATA)."""
import random


def maybe_corrupt(packet: bytes, rate: float, rng=random) -> bytes:
    """With probability `rate`, flip one random bit in the packet."""
    if rate <= 0 or rng.random() >= rate:
        return packet
    data = bytearray(packet)
    bit = rng.randrange(len(data) * 8)
    data[bit // 8] ^= 1 << (bit % 8)
    return bytes(data)
