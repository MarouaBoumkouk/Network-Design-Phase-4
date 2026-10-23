# Network Design Project: Phase 2 (RDT 2.2)
Maroua Boumkouk, Matthew Nguyen, Oluchukwu Okeke 

## Overview
Phase 2 adds RDT 2.2 on top of the Phase 1 UDP file transfer. It uses a checksum, alternating 0/1 sequence numbers, and ACKs only (no NAKs), with stop-and-wait sending. It covers three options: no errors, ACK bit-errors, and DATA bit-errors.

## Team
| Name | Email | Primary responsibility |
|---|---|---|
| Maroua Boumkouk | Maroua_Boumkouk@student.uml.edu | Design document, `maybe_drop()` in `corruption.py`, tests (`test_rdt.py`), README, final check of all deliverables |
| Matthew Nguyen | Matthew_Nguyen@student.uml.edu | `sender.py` (countdown timer, Option 4 ACK loss), demo video |
| Oluchi Okeke | Oluchi_Okeke@student.uml.edu | `receiver.py` (Option 5 DATA loss), experiments and plot (`run_experiments.py`, `plot_results.py`) |

## Demo Video
- **YouTube (unlisted):** 

---

## Repository Structure
```
src/       packet.py (header + checksum), corruption.py (bit flips + drops), sender.py, receiver.py
scripts/   test_rdt.py, run_experiments.py, plot_results.py
docs/      DESIGN_DOCUMENT.md
results/   raw_times.csv, avg_times.csv, completion_time.png
data/      small.bmp (390 KB test image)
README.md
```

## Requirements
- Python 3.12+ (tested on 3.12 macOS and 3.13 Linux)
- Transfer code: standard library only (`socket`, `struct`, `argparse` , `time`, `random`)
- Plot only: `pip install matplotlib`

---


## What's new in Phase 3
- **Countdown timer (sender):** starts when a packet is sent, stops on a valid ACK. If it runs out, the sender resends the same packet and restarts the timer. Timeout: TODO ms.
- **Bad ACKs:** a corrupt or wrong ACK is now ignored. The sender waits for the timer instead of resending right away (matches the RDT 3.0 FSM).
- **Loss injection:** `maybe_drop(rate)` in `corruption.py` returns True with chance `rate`. A dropped packet is just ignored.
  - Option 4 drops ACKs at the sender.
  - Option 5 drops DATA at the receiver (no ACK is sent).
- **END retries are capped** so the sender can't loop forever if the receiver has already closed.

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

## Running the three options
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
Expected: sender prints `corrupt ACK -> resend`, receiver prints `duplicate ... -> resend last ACK`.

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
This checks the packet round trip, checks that every single-bit flip is caught by the checksum, and runs Option 1 at 0% and Options 2 and 3 at 30% and 90%, comparing SHA-256 each time.

## Reproducing the plot
From the repo root:
```bash
python scripts/run_experiments.py      # 5 options x 20 rates x 5 runs (takes a while)
python scripts/plot_results.py
```
- Rates: 0% to 95% in steps of 5%.
- Each point is the average of 5 runs.
- Printing is off during timing.
- Every run is checked with SHA-256.
- Output: `results/raw_times.csv`, `results/avg_times.csv`, `results/completion_time.png`.

## Results
![Completion time vs error rate](results/completion_time.png)

- **Option 1** stays flat (about 0.11 s), since there are no errors.
- **Options 2 and 3** follow about 1/(1−p): small change up to ~30%, then fast growth. 95% takes about 13× longer than 0% (1.5 s vs 0.11 s).
- Options 2 and 3 cost about the same, because either way one bad packet costs one extra DATA + ACK round trip.

---

## Known Issues / Limitations
- Stop-and-wait only (no pipelining), so throughput is low at high error/loss rates.
- The timeout is fixed (TODO ms), not adaptive like TCP. It is tuned for localhost.
- We kept our Phase 2 change to the textbook `oncethru` rule: the receiver always resends its last ACK (starting as ACK 1). See the design doc.
- The receiver stays open for a short time after END in case its last ACK is lost or corrupted. The sender caps END retries so it can still finish.

## Academic Integrity / External Tools
Debugging tools and LLMs may be used for learning and troubleshooting. Final implementation decisions and understanding are our own.
