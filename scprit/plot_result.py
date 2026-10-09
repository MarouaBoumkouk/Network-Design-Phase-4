"""Plot average completion time vs error rate for Options 1-3.

Usage (from the repo root, after run_experiments.py):
    python scripts/plot_results.py
Reads results/avg_times.csv, writes results/completion_time.png.
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")

rates, avg = [], {1: [], 2: [], 3: []}
with open(os.path.join(RESULTS, "avg_times.csv")) as f:
    for row in csv.DictReader(f):
        rates.append(int(row["rate_percent"]))
        for o in (1, 2, 3):
            avg[o].append(float(row[f"option{o}_avg_s"]))

lines = {
    1: ("Option 1: no errors", "#2a78d6", "o"),
    2: ("Option 2: ACK bit-errors", "#eb6834", "s"),
    3: ("Option 3: DATA bit-errors", "#1baf7a", "^"),
}

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
for o, (label, color, marker) in lines.items():
    ax.plot(rates, avg[o], color=color, marker=marker, markersize=6,
            linewidth=2, label=label)

ax.set_xticks(rates)
ax.set_xlabel("Error rate (%)")
ax.set_ylabel("Completion time (s), average of 5 runs")
ax.set_title("RDT 2.2 completion time vs bit-error rate")
ax.grid(True, color="#e3e3e0", linewidth=0.8)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()

out = os.path.join(RESULTS, "completion_time.png")
fig.savefig(out)
print(f"saved {out}")