"""RDT 2.2 sender (Kurose/Ross Figure 3.13).

States:
    Wait for call 0 from above -> send DATA seq 0 -> Wait for ACK 0
    Wait for ACK 0: corrupt or ACK 1 -> resend; good ACK 0 -> Wait for call 1
    Wait for call 1 from above -> send DATA seq 1 -> Wait for ACK 1
    Wait for ACK 1: corrupt or ACK 0 -> resend; good ACK 1 -> Wait for call 0

Option 2 flips bits in received ACKs here, on the sender's receive path.

Usage (from src/):
    python sender.py --option 1
    python sender.py --option 2 --error-rate 0.2
"""
import argparse
import socket
import time

from packet import (TYPE_ACK, TYPE_DATA, TYPE_END, extract_packet, is_corrupt,
                    make_packet)
from corruption import maybe_corrupt

CHUNK_SIZE = 1024
RECV_BUFFER_SIZE = 2048
SAFETY_TIMEOUT = 10.0  # not an RDT timer: only stops the program if the receiver dies


def send_file(path, host="127.0.0.1", port=9000, option=1, error_rate=0.0, quiet=False):
    """Send one file with RDT 2.2. Returns (elapsed_seconds, stats)."""
    ack_error_rate = error_rate if option == 2 else 0.0
    log = (lambda *a: None) if quiet else print

    with open(path, "rb") as f:
        data = f.read()
    chunks = [data[i:i + CHUNK_SIZE] for i in range(0, len(data), CHUNK_SIZE)]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(SAFETY_TIMEOUT)
    dest = (host, port)
    stats = {"packets": len(chunks) + 1, "sent": 0, "resent": 0, "bad_acks": 0}

    start = time.perf_counter()
    seq = 0
    # the END packet goes through the same stop-and-wait steps as DATA
    for i, chunk in enumerate(chunks + [None]):
        # Wait for call `seq` from above: make_pkt + udt_send
        if chunk is None:
            sndpkt = make_packet(TYPE_END, seq)
        else:
            sndpkt = make_packet(TYPE_DATA, seq, chunk)
        sock.sendto(sndpkt, dest)
        stats["sent"] += 1
        log(f"[send] pkt {i} seq={seq}")

        # Wait for ACK `seq`
        while True:
            try:
                rcvpkt, _ = sock.recvfrom(RECV_BUFFER_SIZE)
            except socket.timeout:
                sock.close()
                raise RuntimeError("no reply from receiver (is it running?)")
            rcvpkt = maybe_corrupt(rcvpkt, ack_error_rate)

            if is_corrupt(rcvpkt):
                log(f"[send] corrupt ACK -> resend seq={seq}")
                bad = True
            else:
                pkt_type, _, ack, _ = extract_packet(rcvpkt)
                bad = pkt_type != TYPE_ACK or ack != seq
                if bad:
                    log(f"[send] ACK {ack} but waiting for ACK {seq} -> resend")

            if not bad:
                log(f"[send] got ACK {seq}")
                break
            stats["bad_acks"] += 1
            stats["resent"] += 1
            stats["sent"] += 1
            sock.sendto(sndpkt, dest)

        seq = 1 - seq

    elapsed = time.perf_counter() - start
    sock.close()
    log(f"[send] done: {len(data)} bytes, {stats['packets']} packets, "
        f"{stats['resent']} resends, {elapsed:.3f} s")
    return elapsed, stats


def main():
    p = argparse.ArgumentParser(description="RDT 2.2 sender")
    p.add_argument("--file", default="../data/small.bmp")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=9000)
    p.add_argument("--option", type=int, choices=[1, 2, 3], default=1,
                   help="1=no errors, 2=ACK bit-errors (here), 3=DATA bit-errors (receiver)")
    p.add_argument("--error-rate", type=float, default=0.0,
                   help="chance (0-1) that an ACK gets a bit flipped; Option 2 only")
    p.add_argument("--quiet", action="store_true")
    a = p.parse_args()
    send_file(a.file, a.host, a.port, a.option, a.error_rate, a.quiet)


if __name__ == "__main__":
    main()
