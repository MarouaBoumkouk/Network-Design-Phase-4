# Network-Design-Phase-2
Maroua Boumkouk
Matthew Nguyen 
Oluchukwu okeke


## Overview
This repository implements a UDP/TCP-based file transfer protocol across 6 phases, progressively adding reliability mechanisms and performance evaluation. Phase 2 covers RDT 2.2 over UDP: checksum, alternating 0/1 sequence numbers, ACKs only (no NAKs), and stop-and-wait. It is tested in 3 options: no errors, ACK bit-errors, and DATA bit-errors.
## Team
| Name | Email | Primary responsibility |
|---|---|---|
| Maroua Boumkouk | Maroua_Boumkouk@student.uml.edu | Packet format + checksum (packet.py), bit-error injection (corruption.py), design document
| Matthew Nguyen  | Matthew_Nguyen@student.uml.edu| Sender FSM + Option 2 (`sender.py`), demo video, [design document] |
| Oluchukwu okeke| Oluchukwu_okeke@student.uml.edu | Receiver FSM + Option 3 (`receiver.py`), experiments + plot (`run_experiments.py`, `plot_results.py`) |

## Demo Video (submission)
- **Private YouTube link:**  
- 
- 

---

## Repository Structure
```
src/        # packet.py, corruption.py, sender.py, receiver.py
scripts/    # test_rdt.py, run_experiments.py, plot_results.py
docs/       # design document
results/    # received.bmp, raw_times.csv, avg_times.csv, completion_time.png
data/       # small.bmp
README.md 
```
---

## Requirements
- Language/runtime: Python 3.12.4
- OS tested: macOS
- Dependencies:
  - none beyond the Python standard library (`socket`, `struct` , `random `, `argparse`, `time`)
  - plot only: matplotlib ( `pip install matplotlib`)

---
## Standard CLI Interface (required)
Sender and receiver use the same flags. Use the **same** `--option` and `--error-rate` on both sides.
 
| Flag | Meaning | Default |
|---|---|---|
| `--option` | 1 = no errors, 2 = ACK bit-errors, 3 = DATA bit-errors | 1 |
| `--error-rate` | chance (0 to 1) that a packet gets one bit flipped | 0 |
| `--port` | receiver port | 9000 |
| `--quiet` | turn off printing | off |
| `--file` (sender only) | file to send | `../data/small.bmp` |
| `--out` (receiver only) | where to write the file | `../results/received.bmp` |
 
### Injection / timing / windowing flags
- **Injection:** `--option` and `--error-rate`. Option 2 flips bits in ACKs at the sender. Option 3 flips bits in DATA at the receiver.
- **Timing:** done by `scripts/run_experiments.py` (no flag needed).
- **Windowing:** not used. RDT 2.2 is stop-and-wait.
---
 
## Quick Start (Run Locally)
### Start Receiver
From inside `src/`:
```bash
python receiver.py --option 1
```
 
### Run Sender
From inside `src/` (second terminal, after the receiver is running):
```bash
python sender.py --option 1
```
 
---
 
## Required Demo Scenarios (Current Phase)
Provide the exact commands used to demonstrate each required scenario.
 
### Option 1: No errors
Receiver:
```bash
python receiver.py --option 1
```
Sender:
```bash
python sender.py --option 1
```
Expected behavior:
- Every packet is ACKed the first time, 0 resends. Output file matches the input.
### Option 2: ACK bit-errors (example 20%)
Receiver:
```bash
python receiver.py --option 2 --error-rate 0.2
```
Sender:
```bash
python sender.py --option 2 --error-rate 0.2
```
Expected behavior:
- Sender prints `corrupt ACK -> resend`. Receiver prints `duplicate ... -> resend last ACK` and doesn't write the packet twice. Output file still matches the input.
### Option 3: DATA bit-errors (example 20%)
Receiver:
```bash
python receiver.py --option 3 --error-rate 0.2
```
Sender:
```bash
python sender.py --option 3 --error-rate 0.2
```
Expected behavior:
- Receiver prints `corrupt packet -> resend last ACK`. Sender prints `ACK x but waiting for ACK y -> resend`. Output file still matches the input.
### Checking the file
From inside `src/`:
```bash
shasum -a 256 ../data/small.bmp ../results/received.bmp
```
Both hashes should be the same.
 
### Tests
From the repo root:
```bash
python scripts/test_rdt.py
```
Checks the packet round trip, checks that the checksum catches every 1-bit error, and runs all 3 options with a hash check.
 
---
 
## Figures / Plots (if required by phase)
From the repo root:
```bash
python scripts/run_experiments.py
python scripts/plot_results.py
```
- Error rates 0% to 95% in steps of 5%, 5 runs each, for all 3 options. Takes about 2–3 minutes.
- Printing is turned off while timing.
- Output: `results/completion_time.png` (plot), `results/avg_times.csv`, `results/raw_times.csv`.
![Completion time vs error rate](results/completion_time.png)
 
- Option 1 stays flat, since there are no errors.
- Options 2 and 3 stay close to flat at low error rates, then grow fast near 95%, because each packet needs more tries (about 1/(1−p)).
- Options 2 and 3 take about the same time. Either way, one bad packet costs one extra DATA + ACK round trip.
---
 
## Known Issues / Limitations
- RDT 2.2 assumes no packet loss, so there is no timer. A 10 s safety timeout only stops the sender if the receiver isn't running; it does not resend (that comes in RDT 3.0).
- The receiver always resends its last ACK (starting as ACK 1) instead of using the textbook's `oncethru`, so a corrupt first packet can't get stuck. See the design doc, section 3.1.
- The receiver stays open 2 s after END in case its last ACK got corrupted.
- We used a smaller copy of the Phase 1 photo (`data/small.bmp`, 390 KB) so the 300 timed runs finish quickly.
---
 
## Academic Integrity / External Tools
Debugging tools (IDE debugger, logging) and LLMs may be used for learning and troubleshooting. Final implementation decisions and understanding are our own.
