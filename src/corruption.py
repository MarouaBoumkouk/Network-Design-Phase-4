import random


def maybe_corrupt(packet: bytes, rate: float) -> bytes:
    """With chance `rate`, flip one random bit in the packet."""
    if rate <= 0 or random.random() >= rate:
        return packet
    data = bytearray(packet)
    bit = random.randrange(len(data) * 8)
    data[bit // 8] ^= 1 << (bit % 8)
    return bytes(data)