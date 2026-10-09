import socket
import argparse
from packet import TYPE_END, extract_packet, is_corrupt, make_ack 
from corruption import maybe_corrupt

PORT = 9000
OUT_FILE = "../results/received.bmp"
RECV_BUFFER_SIZE = 2048  
LINGER = 2.0  # seconds to keep answering after END, in case our last ACK got corrupted

def receive_file(out_path=OUT_FILE, port=PORT, option=1, error_rate=0.0, quiet=False,
                 sock=None, linger=LINGER):
    """Receive one file with RDT 2.2 and write it to out_path."""
    data_error_rate = error_rate if option == 3 else 0.0   # Option 3 only
    log = (lambda *a: None) if quiet else print

    if sock is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", port))
        log(f"Receiver listening on port {port}, writing to {out_path}")

    expected = 0             # which seq we're waiting for (0 or 1)
    sndpkt = make_ack(1)     # last ACK sent (starts as ACK 1 so a bad first packet can't get stuck)
    total_packets = 0
    total_bytes = 0
    done = False
    
    with open(out_path, "wb") as out:
        while True:
            try:
                rcvpkt, addr = sock.recvfrom(RECV_BUFFER_SIZE)
            except socket.timeout:
                break        # only happens after END, when the sender stops talking

            rcvpkt = maybe_corrupt(rcvpkt, data_error_rate)   # Option 3: maybe flip a bit

            # damaged packet -> resend last ACK
            if is_corrupt(rcvpkt):
                log("Corrupt packet -> resend last ACK")
                sock.sendto(sndpkt, addr)
                continue

            pkt_type, seq, _, payload = extract_packet(rcvpkt)

            # duplicate (wrong seq) -> resend last ACK, don't write again
            if seq != expected:
                log(f"Duplicate seq={seq} -> resend last ACK")
                sock.sendto(sndpkt, addr)
                continue

            # good packet with the right seq
            if pkt_type == TYPE_END:
                done = True
            else:
                out.write(payload)
                total_packets += 1
                total_bytes += len(payload)

            sndpkt = make_ack(seq)
            sock.sendto(sndpkt, addr)
            log(f"Received seq={seq} -> ACK {seq}")
            expected = 1 - expected     # flip 0 <-> 1

            if done:
                sock.settimeout(linger)  # wait a bit in case END gets resent

    sock.close()
    log(f"Transfer complete: {total_packets} packets, {total_bytes} bytes")
    return {"packets": total_packets, "bytes": total_bytes}


def main():
    p = argparse.ArgumentParser(description="RDT 2.2 receiver")
    p.add_argument("--out", default=OUT_FILE)
    p.add_argument("--port", type=int, default=PORT)
    p.add_argument("--option", type=int, choices=[1, 2, 3], default=1,
                   help="1=no errors, 2=ACK bit-errors (sender), 3=DATA bit-errors (here)")
    p.add_argument("--error-rate", type=float, default=0.0,
                   help="chance (0-1) a DATA packet gets a bit flipped; Option 3 only")
    p.add_argument("--quiet", action="store_true")
    a = p.parse_args()
    receive_file(a.out, a.port, a.option, a.error_rate, a.quiet)


if __name__ == "__main__":
    main()


