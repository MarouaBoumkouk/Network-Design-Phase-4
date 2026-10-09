# sender.py
import time
import socket
import argparse
from packet import (
    make_packet,
    extract_packet,
    is_corrupt,
    TYPE_DATA,
    TYPE_END,
    TYPE_ACK,
)
from corruption import maybe_corrupt


HOST = "127.0.0.1"
PORT = 9000
FILE = "../data/sample.bmp"
CHUNK_SIZE = 1024

#Choose the corruption percentage
parser = argparse.ArgumentParser()
parser.add_argument("--option", type = int, default = 2)
parser.add_argument("--error_rate" , type = float, default = 0.2)
parser.add_argument("--quiet", action ="store_true")

args = parser.parse_args()
QUIET = args.quiet

def log(message):
    if not QUIET:
        print(message)

OPTION = args.option
ERROR_RATE = args.error_rate

RECV_BUFFER_SIZE = 2048

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0)  # Set a timeout for receiving ACKs

seq = 0
total_bytes = 0
packet_count = 0

start_time = time.perf_counter()
with open(FILE, "rb") as f:
    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            break

        pkt = make_packet(TYPE_DATA, seq, chunk)

        while True:
            sock.sendto(pkt, (HOST, PORT))
            log(f"Sent Data packet {seq}")

            try:
                ack_data, addr = sock.recvfrom(RECV_BUFFER_SIZE)
            except socket.timeout:
                log("Timeout - Resending data")
                continue

            #option 2 - corrupt ACK after recieving it 
            if OPTION == 2:
                ack_data = maybe_corrupt(ack_data, ERROR_RATE)

            #check if ACK is corrupt
            if is_corrupt(ack_data):
                log(f"Corrupted ACK detected - Resending data")
                continue
            
            #Extract ACK info
            ack_type, ack_seq, ack_num, payload = extract_packet(ack_data)

            #Check if ACK is valid
            if ack_type == TYPE_ACK and ack_num == seq:
                log(f"Valid ACK {seq} recieved")
                break 
            
            log(f"Incorrect ACK received - Resending data")
        total_bytes += len(chunk)
        packet_count += 1
        seq = 1 - seq

    
#END packet
end_pkt = make_packet(TYPE_END, seq, b"")

while True: 
    #Send END packet
    sock.sendto(end_pkt, (HOST, PORT))
    log(f"Sent END packet {seq}")

    #Wait for ACK
    try:
        ack_data, addr = sock.recvfrom(RECV_BUFFER_SIZE)
    except socket.timeout:
        log(f"Timeout - Resending END packet")
        continue

    #option 2 - Simulate corruption
    if OPTION == 2:
        ack_data = maybe_corrupt(ack_data, ERROR_RATE)

    #check for corruption
    if is_corrupt(ack_data):
        log(f"Corrupted END ACK - Resending END packet")
        continue

    #Extract ACK info
    ack_type, ack_seq, ack_num, payload = extract_packet(ack_data)

    #Check if ACK is valid
    if ack_type == TYPE_ACK and ack_num == seq:
        log(f"Valid END ACK {seq} recieved")
        break

    log(f"Incorrect END ACK - resending END packet")

sock.close()
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Transfer time: {elapsed_time:.4f} seconds")
print(f"Transfer complete: {packet_count} packets, {total_bytes} bytes")

