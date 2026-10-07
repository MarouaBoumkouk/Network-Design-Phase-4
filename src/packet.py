import struct

TYPE_DATA = 0
TYPE_END = 1

HEADER_FORMAT = ">BIBHH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 10


def make_packet(pkt_type: int, seq: int, payload: bytes) -> bytes:
     """Build one wire-format packet: header + payload."""
     header = struct.pack(HEADER_FORMAT, pkt_type, seq, 0, len(payload), 0)
     return header + payload


def extract_packet(packet: bytes):
     """Parse a wire-format packet back into (pkt_type, seq, payload)."""
     header = packet[:HEADER_SIZE]
     payload = packet[HEADER_SIZE:]
     pkt_type, seq, ack, length, checksum = struct.unpack(HEADER_FORMAT, header)
     return pkt_type, seq, payload