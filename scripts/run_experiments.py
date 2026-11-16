"""Time the file transfer for Options 1-5 at error/loss rates 0%..95% (5 runs each).

Runs the receiver in a thread and the sender in the main thread, with all
printing turned off so it doesn't slow the timing. Every run is checked with
SHA-256 so we know the file still arrives correctly.

    1 = no errors/loss
    2 = ACK bit-errors   (sender)
    3 = DATA bit-errors  (receiver)
    4 = ACK loss         (sender)
    5 = DATA loss        (receiver)

Usage (from the repo root):
    python scripts/run_experiments.py
    python scripts/run_experiments.py --options 1 2 3 --runs 5 --file data/small.bmp
Writes results/raw_times.csv and results/avg_times.csv.
"""
import argparse
import csv
import hashlib
import os
import socket
import statistics
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from receiver import receive_file  # noqa: E402
from sender import send_file       # noqa: E402

rates = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55,
         60, 65, 70, 75, 80, 85, 90, 95]
ALL_OPTIONS = (1, 2, 3, 4, 5)


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()



def one_run(in_file, out_file, option, rate, window_size=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))

    port = sock.getsockname()[1]

    t = threading.Thread(
        target=receive_file,
        kwargs=dict(
            out_path=out_file,
            option=option,
            error_rate=rate,
            quiet=True,
            sock=sock,
            linger=0.2
        ),
        daemon=True
    )

    t.start()

    elapsed, stats = send_file(
        in_file,
        "127.0.0.1",
        port,
        option,
        rate,
        quiet=True,
        window_size=window_size
    )

    t.join(timeout=5)

    if t.is_alive():
        raise RuntimeError(
            f"Receiver did not finish: option={option}, rate={rate}"
        )

    return elapsed, stats



def main():
    global rates
    p = argparse.ArgumentParser()
    p.add_argument("--file", default=os.path.join(ROOT, "data", "small.bmp"))
    p.add_argument("--runs", type=int, default=5)
    p.add_argument("--max-rate", type=int,default=85, help="Maximum error/loss rate to test")
    p.add_argument("--min-rate", type=int, default=0,
               help="Minimum error/loss rate to test")
    p.add_argument("--options", type=int, nargs="+", default=list(ALL_OPTIONS),
                   choices=ALL_OPTIONS)
    a = p.parse_args()
    options = sorted(set(a.options))
    rates = [r for r in range(a.min_rate, a.max_rate + 1, 5)]

    results_dir = os.path.join(ROOT, "results")
    os.makedirs(results_dir, exist_ok=True)
    out_file = os.path.join(results_dir, "experiment_out.bmp")
    want = sha256(a.file)

    # times[option][r][k] = completion time for rate index r, run k
    times = {opt: [[0.0] * a.runs for _ in rates] for opt in options}
    raw_rows = []

    for opt in options:
        for r, rate in enumerate(rates):
            for k in range(a.runs):
                elapsed, stats = one_run(a.file, out_file, opt, rate / 100)
                if sha256(out_file) != want:
                    sys.exit(f"output file wrong: option {opt}, rate {rate}%, run {k}")
                times[opt][r][k] = elapsed
                raw_rows.append([opt, rate, k, f"{elapsed:.6f}", stats.get("resent", "")])
            avg = statistics.mean(times[opt][r])
            print(f"option {opt}  rate {rate:2d}%  avg {avg:.4f} s", flush=True)
            with open(os.path.join(results_dir, "progress.csv"),
                      "a", newline="") as f:
                w = csv.writer(f)
                w.writerow([opt, rate, f"{avg:.6f}"])

    with open(os.path.join(results_dir, "raw_times.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["option", "rate_percent", "run", "seconds", "resends"])
        w.writerows(raw_rows)

    with open(os.path.join(results_dir, "avg_times.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rate_percent"] + [f"option{o}_avg_s" for o in options])
        for r, rate in enumerate(rates):
            w.writerow([rate] + [f"{statistics.mean(times[o][r]):.6f}" for o in options])

    os.remove(out_file)
    print("saved results/raw_times.csv and results/avg_times.csv")


if __name__ == "__main__":
    main()
