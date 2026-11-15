"""Phase 1(b) RDT 1.0 receiver (copied from commit 90958b1 in network_design_phase1).

Protocol unchanged: reads "!IH" (seq, len) headers, writes each payload in
arrival order, stops at the empty end-of-transfer packet.

Only change: the code is wrapped in receive_file() so scripts/chart3_phases.py
can time it the same way as Phases 2-4. The original CLI still works:
    python3 receiver.py <output_file>
"""
import socket
import struct
import sys

HOST = "0.0.0.0"
PORT = 9000
HEADER_FORMAT = "!IH"   # seq (4 bytes), len (2 bytes)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
IDLE_TIMEOUT = 10       # added so a lost END marker can't hang the timing script


def receive_file(out_path, port=PORT, quiet=False, sock=None):
    """Receive one file with RDT 1.0 and write it to out_path. Returns stats."""
    log = (lambda *a: None) if quiet else print
    if sock is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((HOST, port))
        log(f"[receiver] listening on port {port}, writing to {out_path}")
    sock.settimeout(IDLE_TIMEOUT)

    packets = 0
    with open(out_path, "wb") as f:
        while True:
            try:
                packet, addr = sock.recvfrom(2048)
            except socket.timeout:
                break
            seq, length = struct.unpack(HEADER_FORMAT, packet[:HEADER_SIZE])
            payload = packet[HEADER_SIZE:HEADER_SIZE + length]
            if length == 0:
                log(f"[receiver] received end-of-transfer marker (seq={seq})")
                break
            f.write(payload)
            packets += 1
            log(f"[receiver] wrote packet seq={seq} ({length} bytes)")

    sock.close()
    log("[receiver] transfer complete")
    return {"delivered": packets}


def main():
    if len(sys.argv) < 2:
        print("usage: python3 receiver.py <output_file>")
        sys.exit(1)
    receive_file(sys.argv[1])


if __name__ == "__main__":
    main()
