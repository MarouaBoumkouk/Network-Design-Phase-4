
"""Graph 2: Go-Back-N window size vs completion time."""

import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")

windows = []
times = []

with open(os.path.join(RESULTS, "window_results.csv")) as f:
    reader = csv.DictReader(f)

    for row in reader:
        windows.append(int(row["window_size"]))
        times.append(float(row["avg_time_s"]))

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)

ax.plot(windows, times, marker="o", linewidth=2,
        color="#2a78d6", label="10% DATA loss")

ax.set_xticks(windows)
ax.set_xlabel("Window Size (packets)")
ax.set_ylabel("Average File Transfer Completion Time (s)")
ax.set_title("Phase 4 Go-Back-N: Completion Time vs Window Size")

ax.grid(True, alpha=0.3)
ax.legend(frameon=False)

fig.tight_layout()

out = os.path.join(RESULTS, "window_size.png")
fig.savefig(out, dpi=300)
plt.close(fig)

print(f"saved {out}")
