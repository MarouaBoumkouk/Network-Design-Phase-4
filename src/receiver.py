"""RDT 3.0 receiver (same FSM as RDT 2.2, Kurose/Ross Figure 3.14).

States:
    Wait for 0 from below: good seq 0 -> deliver, send ACK 0 -> Wait for 1
                           corrupt or seq 1 -> resend last ACK
    Wait for 1 from below: good seq 1 -> deliver, send ACK 1 -> Wait for 0
                           corrupt or seq 0 -> resend last ACK

Option 3 flips bits in received DATA packets here, on the receiver's receive path.
Option 5 drops received DATA packets here (no ACK is sent; the sender times out).

One change from the textbook: the book uses `oncethru` so the receiver sends
nothing if the very first packet is corrupt. With no timer (RDT 2.2 has none),
the sender would then wait forever. So the last ACK starts as ACK 1, and the
receiver always resends it. The sender is waiting for ACK 0, sees ACK 1, and
resends packet 0, which is the same thing the book's FSM wants to happen.

Usage (from src/):
    python receiver.py --option 1
    python receiver.py --option 3 --error-rate 0.2
    python receiver.py --option 5 --error-rate 0.2
"""
import argparse
import socket

from packet import TYPE_END, extract_packet, is_corrupt, make_ack
from corruption import maybe_corrupt, maybe_drop

RECV_BUFFER_SIZE = 2048
LINGER = 2.0  # seconds to keep answering after END, in case our last ACK got corrupted


def receive_file(out_path, port=9000, option=1, error_rate=0.0, quiet=False,
                 sock=None, linger=LINGER):
    """Receive one file with RDT 3.0 and write it to out_path. Returns stats."""
    data_error_rate = error_rate if option == 3 else 0.0
    data_loss_rate = error_rate if option == 5 else 0.0
    log = (lambda *a: None) if quiet else print

    if sock is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", port))
        log(f"[recv] listening on port {port}, writing to {out_path}")

    expected = 0             # state: waiting for `expected` from below
    sndpkt = make_ack(1)     # last ACK sent (see note at top)
    stats = {"delivered": 0, "bytes": 0, "corrupt": 0, "duplicates": 0,
             "dropped": 0}
    done = False

    with open(out_path, "wb") as out:
        while True:
            try:
                rcvpkt, addr = sock.recvfrom(RECV_BUFFER_SIZE)
            except socket.timeout:
                break        # only reached after END, when the sender went quiet
            if maybe_drop(data_loss_rate):
                stats["dropped"] += 1
                log("[recv] DATA lost -> no ACK")
                continue     # as if the packet never arrived
            rcvpkt = maybe_corrupt(rcvpkt, data_error_rate)

            if is_corrupt(rcvpkt):
                stats["corrupt"] += 1
                log(f"[recv] corrupt packet -> resend last ACK")
                sock.sendto(sndpkt, addr)
                continue

            pkt_type, seq, _, payload = extract_packet(rcvpkt)
            if seq != expected:
                stats["duplicates"] += 1
                log(f"[recv] duplicate seq={seq} -> resend last ACK")
                sock.sendto(sndpkt, addr)
                continue

            # good packet with the expected seq: extract, deliver, ACK
            if pkt_type == TYPE_END:
                done = True
            else:
                out.write(payload)
                stats["delivered"] += 1
                stats["bytes"] += len(payload)
            sndpkt = make_ack(seq)
            sock.sendto(sndpkt, addr)
            log(f"[recv] got seq={seq} -> ACK {seq}")
            expected = 1 - expected

            if done:
                # Stay around a bit: if our ACK for END was lost or corrupted the
                # sender will resend END, and we need to ACK it again.
                sock.settimeout(linger)

    sock.close()
    log(f"[recv] done: {stats['delivered']} packets, {stats['bytes']} bytes")
    return stats


def main():
    p = argparse.ArgumentParser(description="RDT 3.0 receiver")
    p.add_argument("--out", default="../results/received.bmp")
    p.add_argument("--port", type=int, default=9000)
    p.add_argument("--option", type=int, choices=[1, 2, 3, 4, 5], default=1,
                   help="1=no errors, 2=ACK bit-errors (sender), 3=DATA bit-errors (here), "
                        "4=ACK loss (sender), 5=DATA loss (here)")
    p.add_argument("--error-rate", type=float, default=0.0,
                   help="chance (0-1) of a DATA bit-error (Option 3) or DATA loss (Option 5)")
    p.add_argument("--quiet", action="store_true")
    a = p.parse_args()
    receive_file(a.out, a.port, a.option, a.error_rate, a.quiet)


if __name__ == "__main__":
    main()
