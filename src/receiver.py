"""Phase 4 Go-Back-N receiver (Kurose/Ross Figure 3.21).

GBN receiver FSM:
    expectedseqnum = 0
    good packet with seq == expectedseqnum -> deliver, expectedseqnum += 1,
                                             send cumulative ACK
    anything else (corrupt, out of order)  -> discard, resend last cumulative ACK
No buffering of out-of-order packets (that's what makes it Go-Back-N).

ACK format: TYPE_ACK packet whose 4-byte `seq` field holds the cumulative ACK
number n = "all packets with seq < n arrived in order; next expected is n".
The 1-byte `ack` field only holds n & 0xFF (it can't hold seq numbers > 255),
so the sender must read the ACK number from the `seq` field:
    pkt_type, ackno, _, _ = extract_packet(rcvpkt)

Option 3 flips bits in received DATA here (receiver's receive path).
Option 5 drops received DATA here (no ACK sent; sender's timer handles it).
Options 1, 2, 4: nothing injected here.

recovery=False (--no-recovery): every arriving packet is written as-is, with
no checksum check, no in-order check, so injected errors/losses show up as a
damaged output file. Used for the "with and without loss recovery" demo.

Usage (from src/):
    python receiver.py --option 1
    python receiver.py --option 3 --error-rate 0.2
    python receiver.py --option 5 --error-rate 0.2 --no-recovery
"""
import argparse
import socket

from packet import TYPE_ACK, TYPE_END, HEADER_SIZE, extract_packet, is_corrupt, make_packet
from corruption import maybe_corrupt, maybe_drop

RECV_BUFFER_SIZE = 2048
LINGER = 2.0         # seconds to keep answering after END, in case our ACK got lost
IDLE_TIMEOUT = 10    # give up if the sender goes silent


def make_cum_ack(n: int) -> bytes:
    """Cumulative ACK n (next expected seq), carried in the 4-byte seq field."""
    return make_packet(TYPE_ACK, n, b"", ack=n & 0xFF)


def receive_file(out_path, port=9000, option=1, error_rate=0.0, quiet=False,
                 sock=None, linger=LINGER, recovery=True):
    """Receive one file with Go-Back-N and write it to out_path. Returns stats."""
    data_error_rate = error_rate if option == 3 else 0.0
    data_loss_rate = error_rate if option == 5 else 0.0
    log = (lambda *a: None) if quiet else print

    if sock is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", port))
        log(f"[recv] listening on port {port}, writing to {out_path}"
            f"{'' if recovery else ' (NO RECOVERY)'}")

    expectedseqnum = 0
    sndpkt = make_cum_ack(0)        # nothing received yet: "next expected is 0"
    stats = {"delivered": 0, "bytes": 0, "corrupt": 0, "out_of_order": 0,
             "dropped": 0}
    done = False
    sock.settimeout(IDLE_TIMEOUT)

    with open(out_path, "wb") as out:
        while True:
            try:
                rcvpkt, addr = sock.recvfrom(RECV_BUFFER_SIZE)
            except socket.timeout:
                break

            # Option 5: DATA loss
            if maybe_drop(data_loss_rate):
                stats["dropped"] += 1
                log("[recv] DATA lost -> no ACK")
                continue
            # Option 3: DATA bit-error
            rcvpkt = maybe_corrupt(rcvpkt, data_error_rate)

            if not recovery:
                if len(rcvpkt) < HEADER_SIZE:
                    continue
                pkt_type, seq, _, payload = extract_packet(rcvpkt)
                sock.sendto(make_cum_ack(seq + 1), addr)
                if pkt_type == TYPE_END:
                    break
                out.write(payload)
                stats["delivered"] += 1
                stats["bytes"] += len(payload)
                continue

            if is_corrupt(rcvpkt):
                stats["corrupt"] += 1
                log(f"[recv] corrupt packet -> resend ACK {expectedseqnum}")
                sock.sendto(sndpkt, addr)
                continue

            pkt_type, seq, _, payload = extract_packet(rcvpkt)
            if seq != expectedseqnum:
                stats["out_of_order"] += 1
                log(f"[recv] seq={seq}, expected {expectedseqnum} -> discard, "
                    f"resend ACK {expectedseqnum}")
                sock.sendto(sndpkt, addr)
                continue

            # in-order, uncorrupted: deliver, advance, ACK
            if pkt_type == TYPE_END:
                done = True
            else:
                out.write(payload)
                stats["delivered"] += 1
                stats["bytes"] += len(payload)
            expectedseqnum += 1
            sndpkt = make_cum_ack(expectedseqnum)
            sock.sendto(sndpkt, addr)
            log(f"[recv] got seq={seq} -> ACK {expectedseqnum}")

            if done:
                sock.settimeout(linger)   # stay to re-ACK a retransmitted END

    sock.close()
    log(f"[recv] done: {stats['delivered']} packets, {stats['bytes']} bytes, "
        f"{stats['corrupt']} corrupt, {stats['out_of_order']} out-of-order, "
        f"{stats['dropped']} dropped")
    return stats


def main():
    p = argparse.ArgumentParser(description="Go-Back-N receiver")
    p.add_argument("--out", default="../results/received.bmp")
    p.add_argument("--port", type=int, default=9000)
    p.add_argument("--option", type=int, choices=[1, 2, 3, 4, 5], default=1,
                   help="1=no errors, 2=ACK bit-errors (sender), 3=DATA bit-errors (here), "
                        "4=ACK loss (sender), 5=DATA loss (here)")
    p.add_argument("--error-rate", type=float, default=0.0,
                   help="chance (0-1) of a DATA bit-error (Option 3) or DATA loss (Option 5)")
    p.add_argument("--no-recovery", action="store_true",
                   help="write packets as they arrive, no checksum/order checks")
    p.add_argument("--quiet", action="store_true")
    a = p.parse_args()
    receive_file(a.out, a.port, a.option, a.error_rate, a.quiet, recovery=not a.no_recovery)


if __name__ == "__main__":
    main()
