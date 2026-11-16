"""Chart 3: completion time of Phase 1, 2, 3 and 4 on the same file (R19).

Each phase's code lives in its own folder and is loaded separately, so their
packet.py / corruption.py files never mix:
    phases/phase1/   RDT 1.0   (no ACKs, no checksum, no timer)
    phases/phase2/   RDT 2.2   (checksum + ACKs, no timer)
    phases/phase3/   RDT 3.0   (adds a countdown timer)
    src/             Phase 4 Go-Back-N (current code)

Fixed settings, all at 10%:
    no errors          Option 1, 0%
    DATA bit-error     Option 3, 10%
    DATA loss          Option 5, 10%
A phase only runs a setting its protocol can recover from. The rest are
marked "not supported" on the chart instead of being timed:
    Phase 1: no errors only (no checksum, so a bit-error corrupts the file
             silently; no timer, so a lost packet is never resent)
    Phase 2: no errors, DATA bit-error (no timer, so a lost packet hangs it)
    Phase 3, Phase 4: all three

Every run is checked with SHA-256 so a wrong file can't be timed.

Usage (from the repo root):
    python3 scripts/chart3_phases.py
    python3 scripts/chart3_phases.py --runs 5 --file data/small.bmp
    python3 scripts/chart3_phases.py --phases 1 2 3     # skip Phase 4
Writes results/chart3_raw.csv, results/chart3_avg.csv, results/chart3_phases.png.
"""
import argparse
import csv
import hashlib
import importlib
import os
import socket
import statistics
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")

PHASE_DIRS = {
    1: os.path.join(ROOT, "phases", "phase1"),
    2: os.path.join(ROOT, "phases", "phase2"),
    3: os.path.join(ROOT, "phases", "phase3"),
    4: os.path.join(ROOT, "src"),
}
# (key, label, option, rate)
SETTINGS = [
    ("none",  "No errors (Option 1)",          1, 0.0),
    ("biterr", "10% DATA bit-error (Option 3)", 3, 0.10),
    ("loss",  "10% DATA loss (Option 5)",      5, 0.10),
]
SUPPORTED = {1: {"none"}, 2: {"none", "biterr"},
             3: {"none", "biterr", "loss"}, 4: {"none", "biterr", "loss"}}
SHARED_MODULES = ("packet", "corruption", "sender", "receiver")


def load_phase(phase):
    """Import one phase's sender/receiver without mixing in other phases' modules."""
    for name in SHARED_MODULES:
        sys.modules.pop(name, None)
    sys.path.insert(0, PHASE_DIRS[phase])
    try:
        sender = importlib.import_module("sender")
        receiver = importlib.import_module("receiver")
    finally:
        sys.path.pop(0)
    return sender.send_file, receiver.receive_file


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def one_run(phase, send_file, receive_file, in_file, out_file, option, rate):
    if os.path.exists(out_file):
        os.remove(out_file)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))             # free port, so runs never mix
    port = sock.getsockname()[1]
    if phase == 1:
        rkw = dict(out_path=out_file, quiet=True, sock=sock)
    else:
        rkw = dict(out_path=out_file, option=option, error_rate=rate,
                   quiet=True, sock=sock, linger=0.2)
    t = threading.Thread(target=receive_file, kwargs=rkw, daemon=True)
    t.start()
    if phase == 1:
        elapsed, _ = send_file(in_file, "127.0.0.1", port, quiet=True)
    else:
        elapsed, _ = send_file(in_file, "127.0.0.1", port, option, rate, quiet=True)
    t.join()
    return elapsed


def plot(avg, phases):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {"none": "#2a78d6", "biterr": "#eb6834", "loss": "#1baf7a"}
    width = 0.26
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
    xs = range(len(phases))
    top = max([v for p in phases for v in avg[p].values() if v is not None] or [1])

    for i, (key, label, _, _) in enumerate(SETTINGS):
        offset = (i - 1) * width
        for x, p in zip(xs, phases):
            v = avg[p].get(key)
            if v is None:
                ax.text(x + offset, top * 0.02, "not\nsupported", ha="center",
                        va="bottom", fontsize=7, color="#6b6b6b")
                continue
            ax.bar(x + offset, v, width - 0.03, color=colors[key],
                   label=label if p == next(q for q in phases if avg[q].get(key) is not None) else None)
            ax.text(x + offset, v + top * 0.01, f"{v:.2f}", ha="center",
                    va="bottom", fontsize=8, color="#3a3a3a")

    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"Phase {p}" for p in phases])
    ax.set_xlabel("Phase")
    ax.set_ylabel("Completion time (s), average of runs")
    ax.set_title("Chart 3: completion time by phase, same file, fixed 10% error / loss")
    ax.grid(True, axis="y", color="#e3e3e0", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    out = os.path.join(RESULTS, "chart3_phases.png")
    fig.savefig(out)
    print(f"saved {out}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", default=os.path.join(ROOT, "data", "small.bmp"))
    p.add_argument("--runs", type=int, default=5)
    p.add_argument("--phases", type=int, nargs="+", default=[1, 2, 3, 4],
                   choices=[1, 2, 3, 4])
    a = p.parse_args()
    phases = sorted(set(a.phases))

    os.makedirs(RESULTS, exist_ok=True)
    out_file = os.path.join(RESULTS, "chart3_out.bmp")
    want = sha256(a.file)

    # times_phase[p][setting][k] = completion time for phase p, run k
    times_phase = {ph: {} for ph in phases}
    avg = {ph: {} for ph in phases}
    raw_rows = []

    for ph in phases:
        send_file, receive_file = load_phase(ph)
        for key, label, option, rate in SETTINGS:
            if key not in SUPPORTED[ph]:
                avg[ph][key] = None
                print(f"Phase {ph}  {label:32s}  not supported")
                continue
            runs = []
            for k in range(a.runs):
                elapsed = one_run(ph, send_file, receive_file, a.file, out_file, option, rate)
                if sha256(out_file) != want:
                    sys.exit(f"output file wrong: Phase {ph}, {label}, run {k}")
                runs.append(elapsed)
                raw_rows.append([ph, key, option, f"{rate:.2f}", k, f"{elapsed:.6f}"])
            times_phase[ph][key] = runs
            avg[ph][key] = statistics.mean(runs)
            print(f"Phase {ph}  {label:32s}  avg {avg[ph][key]:.4f} s", flush=True)

    with open(os.path.join(RESULTS, "chart3_raw.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["phase", "setting", "option", "rate", "run", "seconds"])
        w.writerows(raw_rows)
    with open(os.path.join(RESULTS, "chart3_avg.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["phase"] + [f"{key}_avg_s" for key, *_ in SETTINGS])
        for ph in phases:
            w.writerow([ph] + ["" if avg[ph][key] is None else f"{avg[ph][key]:.6f}"
                               for key, *_ in SETTINGS])

    if os.path.exists(out_file):
        os.remove(out_file)
    print("saved results/chart3_raw.csv and results/chart3_avg.csv")
    plot(avg, phases)


if __name__ == "__main__":
    main()
