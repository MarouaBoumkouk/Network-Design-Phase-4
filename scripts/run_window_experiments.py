
import csv
import os
import statistics

from run_experiments import one_run, sha256, ROOT

WINDOW_SIZES = [1, 2, 5, 10, 20, 50]
LOSS_RATE = 0.10
RUNS = 3

input_file = os.path.join(ROOT, "data", "small.bmp")
results_dir = os.path.join(ROOT, "results")
os.makedirs(results_dir, exist_ok=True)

output_file = os.path.join(results_dir, "window_experiment.bmp")
csv_file = os.path.join(results_dir, "window_results.csv")

expected_hash = sha256(input_file)

with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["window_size", "avg_time_s"])

    for window in WINDOW_SIZES:
        times = []

        for trial in range(RUNS):
            elapsed, stats = one_run(
                input_file,
                output_file,
                option=5,
                rate=LOSS_RATE,
                window_size=window
            )

            if sha256(output_file) != expected_hash:
                raise RuntimeError(
                    f"File mismatch at window {window}"
                )

            times.append(elapsed)

        average = statistics.mean(times)
        writer.writerow([window, average])
        f.flush()

        print(
            f"Window {window}: "
            f"Average {average:.4f} seconds",
            flush=True
        )

print("Saved results/window_results.csv")
