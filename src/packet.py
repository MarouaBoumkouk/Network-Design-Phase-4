import struct

TYPE_DATA = 0
TYPE_END = 1
TYPE_ACK = 2                                   # NEW (step 1)

HEADER_FORMAT = ">BIBHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 10

def checksum(data: bytes) -> int:              # NEW (step 2)
    """16-bit Internet checksum."""
    if len(data) % 2:
        data += b"\x00"
    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) | data[i + 1]
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF

def make_packet(pkt_type: int, seq: int, payload: bytes = b"", ack: int = 0) -> bytes:
     """Build one wire-format packet: header + payload."""
     header = struct.pack(HEADER_FORMAT, pkt_type, seq, 0, len(payload), 0)
     csum = checksum(header + payload)                                          # NEW
     header = struct.pack(HEADER_FORMAT, pkt_type, seq, ack, len(payload), csum)  # NEW
     return header + payload


def extract_packet(packet: bytes):
     """Parse a wire-format packet back into (pkt_type, seq, payload)."""
     header = packet[:HEADER_SIZE]
     payload = packet[HEADER_SIZE:]
     pkt_type, seq, ack, length, checksum = struct.unpack(HEADER_FORMAT, header)
     pkt_type, seq, ack, length, csum = struct.unpack(HEADER_FORMAT, header)   # CHANGED
     return pkt_type, seq, payload
