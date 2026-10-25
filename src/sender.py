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
import random 

from packet import (TYPE_ACK, TYPE_DATA, TYPE_END, extract_packet, is_corrupt,
                    make_packet)
from corruption import maybe_corrupt, maybe_drop

CHUNK_SIZE = 1024
RECV_BUFFER_SIZE = 2048
RDT_TIMEOUT = 0.05 # Waits 0.5 seconds before retransmission 
MAX_END_RETRIES = 50 # stops endless retransmissions


def send_file(path, host="127.0.0.1", port=9000, option=1, error_rate=0.0, quiet=False):
    """Send one file with RDT 2.2. Returns (elapsed_seconds, stats)."""
    ack_error_rate = error_rate if option == 2 else 0.0
    ack_loss_rate = error_rate if option == 4 else 0.0
    log = (lambda *a: None) if quiet else print

    with open(path, "rb") as f:
        data = f.read()
    chunks = [data[i:i + CHUNK_SIZE] for i in range(0, len(data), CHUNK_SIZE)]


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest = (host, port)
    stats = {"packets": len(chunks) + 1, "sent": 0, "resent": 0, "bad_acks": 0}

    start = time.perf_counter()
    seq = 0
    end_retries = 0
    
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

        #start timer
        deadline = time.monotonic() + RDT_TIMEOUT

        # Wait for ACK `seq`
        while True:
            remaining = deadline - time.monotonic()

            #expired time retransmit 
            if remaining <= 0:

                #limits the end retransmission 
                if chunk is None:
                    if end_retries >= MAX_END_RETRIES:
                        log("[send] no ACK for END, receiver must be done")
                    break
                    end_retries += 1

                stats["resent"] += 1 
                stats["sent"] += 1
                sock.sendto(sndpkt, dest)
                log(f"[send] timeout -> resend seq = {seq}")

                #restarting timer
                deadline = time.monotonic() + RDT_TIMEOUT
                continue
            
            #wait for the rest of the time 
            sock.settimeout(remaining)

            try: 
                rcvpkt, _ = sock.recvfrom(RECV_BUFFER_SIZE)
            except socket.timeout:
                continue

            #option 4 simulate ack packet loss 
            if maybe_drop(ack_loss_rate):
                log(f"[send] ACK dropped (option 4) ")
                continue

            # simulate ack corruption 
            rcvpkt = maybe_corrupt(rcvpkt, ack_error_rate)

            #check if ack is corrupted
            if is_corrupt(rcvpkt):
                stats["bad_acks"] += 1
                log(f"[send]corrupt ACK -> keep waiting")
                continue

            #extract info
            pkt_type, _, ack, _ = extract_packet(rcvpkt)

            #check for correct ack
            if pkt_type == TYPE_ACK and ack == seq:
                log(f"[send] got ACK {seq}")
                break 

            #wrong ack
            stats["bad_acks"] += 1 
            log(f"[send] incorrect ACK -> keep waiting")


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
    p.add_argument("--option", type=int, choices=[1, 2, 3, 4, 5], default=1,
                   help="1=no errors, 2=ACK bit-errors (here), 3=DATA bit-errors (receiver), 4=ACK loss, 5=DATA loss")
    p.add_argument("--error-rate", type=float, default=0.0,
                   help="chance (0-1) that an ACK gets a bit flipped; Option 2 only")
    p.add_argument("--quiet", action="store_true")
    a = p.parse_args()
    send_file(a.file, a.host, a.port, a.option, a.error_rate, a.quiet)


if __name__ == "__main__":
    main()
