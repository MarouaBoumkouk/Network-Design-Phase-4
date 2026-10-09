# sender.py
import socket
from packet import make_packet, TYPE_DATA, TYPE_END

HOST = "127.0.0.1"
PORT = 9000
FILE = "../data/sample.bmp"
CHUNK_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
seq = 0
total_bytes = 0
with open(FILE, "rb") as f:
    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            break
        pkt = make_packet(TYPE_DATA, seq, chunk)
        sock.sendto(pkt, (HOST, PORT))
        print(f"Sent packet {seq}, {len(chunk)} bytes")
        total_bytes += len(chunk)
        seq += 1

sock.sendto(make_packet(TYPE_END, seq, b""), (HOST, PORT))
print(f"Transfer complete: {seq} packets, {total_bytes} bytes")