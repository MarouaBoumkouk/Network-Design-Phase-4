import socket
from packet import extract_packet, TYPE_DATA, TYPE_END

PORT = 9000
OUT_FILE = "../results/received.bmp"
RECV_BUFFER_SIZE = 2048  

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("0.0.0.0", PORT))
print(f"Receiver listening on port {PORT}, writing to {OUT_FILE}")

total_bytes = 0
with open(OUT_FILE, "wb") as out:
    while True:
        data, addr = server.recvfrom(RECV_BUFFER_SIZE)
        pkt_type, seq, payload = extract_packet(data)

        if pkt_type == TYPE_END:
            print(f"Transfer complete: {seq} packets, {total_bytes} bytes")
            break

        out.write(payload)
        total_bytes += len(payload)
        print(f"Received packet {seq}, {len(payload)} bytes")