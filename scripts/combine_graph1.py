
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

files = {
    1: "option1_avg.csv",
    2: "option2_avg.csv",
    3: "option3_combined.csv",
    4: "option4_avg.csv",
    5: "option5_avg.csv",
}

fieldnames = ["rate_percent"] + [
    f"option{i}_avg_s" for i in range(1, 6)
]

data = {}

for option, filename in files.items():
    with open(RESULTS / filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rate = int(row["rate_percent"])
            key = f"option{option}_avg_s"

            if rate not in data:
                data[rate] = {"rate_percent": rate}

            data[rate][key] = row[key]

output = RESULTS / "graph1_combined.csv"

with open(output, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for rate in range(0, 100, 5):
        writer.writerow({
            key: data.get(rate, {}).get(key, "")
            for key in fieldnames
        } | {"rate_percent": rate})

print(f"Saved {output}")
