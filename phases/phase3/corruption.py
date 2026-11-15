"""Bit-error and loss injection for Options 2-5."""
import random


def maybe_corrupt(packet: bytes, rate: float, rng=random) -> bytes:
    """With probability `rate`, flip one random bit in the packet."""
    if rate <= 0 or rng.random() >= rate:
        return packet
    data = bytearray(packet)
    bit = rng.randrange(len(data) * 8)
    data[bit // 8] ^= 1 << (bit % 8)
    return bytes(data)

def maybe_drop(rate: float, rng=random) -> bool:
    """Return True with probability `rate` (the packet is treated as lost)."""
    return rate > 0 and rng.random() < rate