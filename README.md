# Network Design Project: Phase 3 (RDT 2.2)
Maroua Boumkouk, Matthew Nguyen, Oluchukwu Okeke 

## Overview
Phase 3 adds RDT 3.0 on top of our Phase 2 RDT 2.2 code. The sender now has a countdown timer, so it can recover from lost packets, not just corrupted ones. It is still stop-and-wait with a checksum, alternating 0/1 sequence numbers, and ACKs only (no NAKs). The receiver is the same as RDT 2.2. It covers five options: no errors, ACK bit-errors, DATA bit-errors, ACK loss, and DATA loss.

## Team
| Name | Email | Primary responsibility |
|---|---|---|
| Maroua Boumkouk | Maroua_Boumkouk@student.uml.edu | Design document, `maybe_drop()` in `corruption.py`, tests (`test_rdt.py`), README, final check of all deliverables |
| Matthew Nguyen | Matthew_Nguyen@student.uml.edu | `sender.py` (countdown timer, Option 4 ACK loss), demo video |
| Oluchi Okeke | Oluchi_Okeke@student.uml.edu | `receiver.py` (Option 5 DATA loss), experiments and plot (`run_experiments.py`, `plot_results.py`) |

## Demo Video
- **YouTube (unlisted):** https://youtu.be/Zv0cYDouGZs

---

## Repository Structure
```
src/       packet.py (header + checksum), corruption.py (bit flips + drops), sender.py, receiver.py
scripts/   test_rdt.py, run_experiments.py, plot_results.py
docs/      DESIGN_DOCUMENT.md
results/   raw_times.csv, avg_times.csv, completion_time.png
data/      small.bmp (390 KB test image), tiny.bmp (small copy, for timing experiments)
README.md
```

## Requirements
- Python 3.12+ (tested on 3.12 macOS and 3.13 Linux)
- Transfer code: standard library only (`socket`, `struct`, `argparse` , `time`, `random`)
- Plot only: `pip install matplotlib`

---


## What's new in Phase 3
- **Countdown timer (sender):** starts when a packet is sent, stops on a valid ACK. If it runs out, the sender resends the same packet and restarts the timer. Timeout: 50 ms.
- **Bad ACKs:** a corrupt or wrong ACK is now ignored. The sender waits for the timer instead of resending right away (matches the RDT 3.0 FSM).
- **Loss injection:** `maybe_drop(rate)` in `corruption.py` returns True with chance `rate`. A dropped packet is just ignored.
  - Option 4 drops ACKs at the sender.
  - Option 5 drops DATA at the receiver (no ACK is sent).
- **END retries are capped (50)** so the sender can't loop forever if the receiver has already closed.
- **Receiver idle timeout (10 s)** so the receiver can't wait forever if the sender gives up.

## CLI
Both programs take the same flags:

| Flag | Meaning | Default |
|---|---|---|
| `--option` | 1 = no errors, 2 = ACK bit-errors, 3 = DATA bit-errors , 4 = ACK loss, 5 = DATA loss| 1 |
| `--error-rate` | chance (0–1) a packet is corrupted (Options 2, 3) or dropped (Options 4, 5) | 0 |
| `--port` | receiver port | 9000 |
| `--quiet` | turn off printing | off |
| `--file` (sender) | file to send | `../data/small.bmp` |
| `--out` (receiver) | where to write it | `../results/received.bmp` |

Use the **same** `--option` and `--error-rate` on both sides. Option 2 and 4 act at the sender (on ACKs). Options 3 and 5 act at the receiver (on DATA).

---
## Running the five options
Run everything from inside `src/`. Start the receiver first, then run the sender in a second terminal.

### Option 1: no errors
```bash
python receiver.py --option 1
python sender.py --option 1
```
Expected: every packet ACKed once, 0 resends.

### Option 2: ACK bit-errors (example 20%)
```bash
python receiver.py --option 2 --error-rate 0.2
python sender.py --option 2 --error-rate 0.2
```
Expected: sender prints \corrupt ACK -> keep waiting`, times out, and resends. Receiver prints `duplicate ... -> resend last ACK`.`

### Option 3: DATA bit-errors (example 20%)
```bash
python receiver.py --option 3 --error-rate 0.2
python sender.py --option 3 --error-rate 0.2
```
Expected: receiver finds the corrupt packet and resends its last ACK. Sender sees the wrong ACK, ignores it, times out, and resends. 
### Option 4: ACK loss (example 20%)
```bash
python receiver.py --option 4 --error-rate 0.2
python sender.py --option 4 --error-rate 0.2
```
Expected: sender drops the ACK, times out, and resends. Receiver sees a duplicate and resends its last ACK.
 
### Option 5: DATA loss (example 20%)
```bash
python receiver.py --option 5 --error-rate 0.2
python sender.py --option 5 --error-rate 0.2
```
Expected: receiver drops the packet and sends nothing. Sender times out and resends.

### Check the file
```bash
cmp ../data/small.bmp ../results/received.bmp && echo SAME
```
You can also just open `results/received.bmp`.

---

## Tests
From the repo root:
```bash
python scripts/test_rdt.py
```
...checks \maybe_drop()`, and runs Option 1 at 0% and Options 2–5 at 30% and 50%, comparing SHA-256 each time.`

## Reproducing the plot
From the repo root:
```bash
python scripts/run_experiments.py --file data/tiny.bmp   # about 45 min    # 5 options x 20 rates x 5 runs (takes a while)
python scripts/plot_results.py
```
add: - We use \tiny.bmp` for timing so the 500 runs finish in under an hour. With `small.bmp` it would take about 5 hours.`
- Rates: 0% to 95% in steps of 5%.
- Each point is the average of 5 runs.
- Printing is off during timing.
- Every run is checked with SHA-256.
- Output: `results/raw_times.csv`, `results/avg_times.csv`, `results/completion_time.png`.

## Results
![Completion time vs error/loss rate](results/completion_time.png)

File: `data/tiny.bmp`, timeout 50 ms, each point = average of 5 runs.

| Rate | Opt 1 | Opt 2 | Opt 3 | Opt 4 | Opt 5 |
|---|---|---|---|---|---|
| 0% / 30% | 0.009 s | 0.56 s | 0.81 s | 0.66 s | 0.66 s |
| 50% | 0.010 s | 1.28 s | 1.44 s | 1.36 s | 1.74 s |
| 80% | 0.009 s | 5.92 s | 6.65 s | 5.45 s | 5.51 s |
| 95% | 0.009 s | 29.54 s | 24.58 s | 27.67 s | 27.61 s |

- **Option 1** stays flat (about 0.01 s), since nothing goes wrong.
- **Options 2-5 all grow like p/(1-p):** slow at first, then very fast after about 70%. At 95%, each packet needs about 20 tries on average, so the transfer is about 3000x slower than Option 1.
- **All four error/loss options cost about the same.** In RDT 3.0 the sender ignores bad or wrong ACKs and waits for the timeout, so a corrupted packet and a lost packet both cost one 50 ms timeout. The timeout is much bigger than the round trip on localhost, so it is what sets the time.
- The small differences between Options 2-5 (for example at 95%) come from randomness. With only 5 runs per point, a few unlucky retries change the average a lot.

---

## Known Issues / Limitations
- Stop-and-wait only (no pipelining), so throughput is low at high error/loss rates.
- The timeout is fixed (50 ms), not adaptive like TCP. It is tuned for localhost.
- We kept our Phase 2 change to the textbook `oncethru` rule: the receiver always resends its last ACK (starting as ACK 1). See the design doc.
- The receiver stays open for a short time after END in case its last ACK is lost or corrupted. The sender caps END retries so it can still finish.

## Academic Integrity / External Tools
Debugging tools and LLMs may be used for learning and troubleshooting. Final implementation decisions and understanding are our own.
