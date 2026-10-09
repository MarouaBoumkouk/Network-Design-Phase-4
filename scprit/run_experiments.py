import csv, os, socket, sys, threading, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from receiver import receive_file
from sender import send_file

FILE = os.path.join(ROOT, "data", "small.bmp")
OUT = os.path.join(ROOT, "results", "experiment_out.bmp")
rates = range(0, 100, 5)          # 0, 5, 10, ... 95

def one_run(option, rate):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))   # any free port
    port = sock.getsockname()[1]
    # start the receiver in the background
    t = threading.Thread(target=receive_file, kwargs=dict(
        out_path=OUT, option=option, error_rate=rate, quiet=True, sock=sock, linger=0.2))
    t.start()
    # run the sender and time it
    seconds, _ = send_file(FILE, "127.0.0.1", port, option, rate, quiet=True)
    t.join()
    return seconds

with open(os.path.join(ROOT, "results", "avg_times.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rate_percent", "option1_avg_s", "option2_avg_s", "option3_avg_s"])
    for rate in rates:
        row = [rate]
        for option in (1, 2, 3):
            times = [one_run(option, rate / 100) for _ in range(5)]   # 5 runs
            row.append(statistics.mean(times))
        w.writerow(row)
        print(rate, row[1:])