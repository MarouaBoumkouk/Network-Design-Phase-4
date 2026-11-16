"""Plot average completion time vs error/loss rate for Options 1-5.

Usage (from the repo root, after run_experiments.py):
    python scripts/plot_results.py
Reads results/avg_times.csv, writes results/completion_time.png.
Plots whichever option columns are in the CSV.
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")

lines = {
    1: ("Option 1: no errors/loss", "#2a78d6", "o"),
    2: ("Option 2: ACK bit-errors", "#eb6834", "s"),
    3: ("Option 3: DATA bit-errors", "#1baf7a", "^"),
    4: ("Option 4: ACK loss", "#8a4fd8", "D"),
    5: ("Option 5: DATA loss", "#d6455d", "v"),
}

rates, avg = [], {}
with open(os.path.join(RESULTS, "option3_combined.csv")) as f:    
    reader = csv.DictReader(f)
    options = [o for o in lines if f"option{o}_avg_s" in reader.fieldnames]
    for o in options:
        avg[o] = []
    for row in reader:
        rates.append(int(row["rate_percent"]))
        for o in options:
            avg[o].append(float(row[f"option{o}_avg_s"]))

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
for o in options:
    label, color, marker = lines[o]
    ax.plot(rates, avg[o], color=color, marker=marker, markersize=6,
            linewidth=2, label=label)

ax.set_xticks(rates)
ax.set_xlabel("Error / loss rate (%)")
ax.set_ylabel("Average file transfer completion time (s)")
ax.set_title("Phase 4 Go-Back-N: Completion Time vs Error/Loss Rate")

ax.grid(True, color="#e3e3e0", linewidth=0.8)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()

out = os.path.join(RESULTS, "completion_time.png")
fig.savefig(out)
print(f"saved {out}")
