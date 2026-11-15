"""Phase 1(b) RDT 1.0 sender (copied from commit 90958b1 in network_design_phase1).

Protocol unchanged: header "!IH" (seq, len), 1024-byte payloads, a 1 ms pause
between packets, and an empty packet (len=0) as the end-of-transfer marker.
No ACKs, no checksum, no timer.

Only change: the code is wrapped in send_file() so scripts/chart3_phases.py
can time it the same way as Phases 2-4. The original CLI still works:
    python3 sender.py <input_file>
"""
import socket
import struct
import sys
import time

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000
PACKET_SIZE = 1024
HEADER_FORMAT = "!IH"


def send_file(path, host=SERVER_HOST, port=SERVER_PORT, quiet=False):
    """Send one file with RDT 1.0. Returns (elapsed_seconds, stats)."""
    log = (lambda *a: None) if quiet else print
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start = time.perf_counter()
    seq = 0
    with open(path, "rb") as f:
        while True:
            chunk = f.read(PACKET_SIZE)
            if not chunk:
                break
            header = struct.pack(HEADER_FORMAT, seq, len(chunk))
            sock.sendto(header + chunk, (host, port))
            log(f"[sender] sent packet seq={seq} ({len(chunk)} bytes)")
            seq += 1
            time.sleep(0.001)  # tiny delay to avoid overrunning the receiver's socket buffer

    sock.sendto(struct.pack(HEADER_FORMAT, seq, 0), (host, port))
    log(f"[sender] sent end-of-transfer marker (seq={seq})")
    elapsed = time.perf_counter() - start
    sock.close()
    log("[sender] done")
    return elapsed, {"packets": seq + 1, "resent": 0}


def main():
    if len(sys.argv) < 2:
        print("usage: python3 sender.py <input_file>")
        sys.exit(1)
    send_file(sys.argv[1])


if __name__ == "__main__":
    main()
