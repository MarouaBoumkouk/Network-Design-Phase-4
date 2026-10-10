"""Packet format for Phase 2 (RDT 2.2).

Same 10-byte header as Phase 1, but now the ack and checksum fields are used.

    type     1 byte   0=DATA, 1=END, 2=ACK
    seq      4 bytes  alternating bit, 0 or 1
    ack      1 byte   for ACK packets: the seq number being ACKed
    len      2 bytes  payload length
    checksum 2 bytes  16-bit Internet checksum over header + payload
"""
import struct

TYPE_DATA = 0
TYPE_END = 1
TYPE_ACK = 2

HEADER_FORMAT = ">BIBHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 10


def checksum(data: bytes) -> int:
    """16-bit one's complement sum (Internet checksum)."""
    if len(data) % 2:
        data += b"\x00"
    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) | data[i + 1]
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


def make_packet(pkt_type: int, seq: int, payload: bytes = b"", ack: int = 0) -> bytes:
    """Build header + payload, with the checksum filled in."""
    header = struct.pack(HEADER_FORMAT, pkt_type, seq, ack, len(payload), 0)
    csum = checksum(header + payload)
    header = struct.pack(HEADER_FORMAT, pkt_type, seq, ack, len(payload), csum)
    return header + payload


def make_ack(seq: int) -> bytes:
    return make_packet(TYPE_ACK, seq, b"", ack=seq)


def is_corrupt(packet: bytes) -> bool:
    """True if the packet is too short, has a bad length, or fails the checksum."""
    if len(packet) < HEADER_SIZE:
        return True
    _, _, _, length, _ = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])
    if length != len(packet) - HEADER_SIZE:
        return True
    # Summing a packet that already holds its checksum gives 0 if nothing changed.
    return checksum(packet) != 0


def extract_packet(packet: bytes):
    """Return (pkt_type, seq, ack, payload). Call is_corrupt() first."""
    pkt_type, seq, ack, length, _ = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])
    return pkt_type, seq, ack, packet[HEADER_SIZE:HEADER_SIZE + length]
