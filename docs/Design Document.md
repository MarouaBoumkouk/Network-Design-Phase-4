## Network Design Project - Phase Proposal and Design Document (Phase 2 of 5)
**Purpose:**  
**Names:** Maroua Boumkouk Matthew Nguyen   
**GitHub Repo URL (with GitHub usernames):**  https://github.com/MattN11/Network-Design-Phase-2
**Phase:** 2  
**Submission Date:** Friday 09 October 2026 
**Version:** (1)

## 0) Executive Summary 
   For Phase 2, our team will build off of our previous UDP transfer file project but implementing the Reliable Data Transfer 2.2 Protocol. This phase will focus on detecting corrupted packets, acknowledgements, and recover through retransmission. Our implementation uses alternating sequence numbers, checksums, and acknowledgement to make sure the file is transferred correctly. 

We will test three scenarios:
1. File transfer with no errors
2. ACK bit corruption at the sender.
3. DATA bit corruption at the receiver

## 1) Phase requirements
### 1.1 Demo deliverable
- **Private YouTube link:**  


### 1.2 Required demo scenarios
| Option | Scenario | Expected Result|
|---|---|---|
| 1 | No Errors | File tansfers succesfully |
| 2 | ACK bit corruption | Sender detects corrupted ACKs and retransmits DATA packets |
| 3 | DATA bit corruption | Receiver detects corrupted DATA packets and resends its previous ACK |

We will also verify that the original and receive file have matching SHA-256 hashes.

### 1.3 Required figures / plots

We will generate performance graphs showing how packet corruption affects file transfer time.

Phase 2 will use:
- Corruption rates from **0% to 95%**
- Increments of **5%**
- **5 trials** per corruption rate
- Average transfer time for each corruption rate
  

## 2) Phase plan (company-style, lightweight)


### 2.1 Scope: what changes/additions this phase

For phase 2, our team will improve our previous UDP file transfer project by implementing the RDT 2.2 protocol

The following features will be added:
- Alternating sequence numbers
- Checksum generation and verification
- Detection of corrupted DATA and ACK packets
- Retransmission when ACK is corrupted or incorrect
- Detection of duplicate packets
- ACK generation and validation
- Simulation of DATA and ACK bit Corruption

  **Out of Scope:**
  - Simulating packet loss as a separate test scenario
  - Sliding window protocols
  - Transferring multiple files simultaneously
     
### 2.2 Acceptance criteria (your checklist)
List 5–10 measurable checks that mean you’re done (examples below).

- [ ] The sender successfully transfers BMP file using UDP 
- [ ] The receiver reconstructs the original file correctly
- [ ] Sequence numbers alternate between 1 and 0
- [ ] Checksums detect corrupted DATA and ACK packets 
- [ ] The sender Retransmits packets when ACK is corrupted  
- [ ] The receiver detects duplicate packets 

### 2.3 Work breakdown (high-level; Person X will work on A, Person Y will work on B...)
Workstream A - Packet Structure and Checksums 
Member will work on packet creation, extraction, and checksum verification  

Workstream B - Sender Implementation 
Member will implement sender sequence numbers, ACK processing, retransmission, and ACK corruption 

Workstream C - Receiver Implementation
Member will implement receiver validation, duplicate evaluation, ACK generation, and Data corruption. 


## 3) Architecture + state diagrams
Your phase specs likely include a reference state diagram. **You should build on it across phases.**


### 3.2 Component responsibilities
- **Sender(sender.py)**
  - responsibilities:  
- **Receiver**
  - responsibilities: 
- **Shared modules/utilities**
  - packet encode/decode: `packet.py`
  - checksum: not used this phase
  - logging/timing: plain 
  - CLI/config parsing: none

### 3.3 Message flow overview


## 4) Packet format (high-level spec)

### 4.1 Packet types



### 4.2 Header fields (this is the “field table”)


| Field | Size (bytes/bits) | Type | Description | Notes |


---

## 5) Data structures + module map

### 5.1 Key data structures


### 5.2 Module map + dependencies


## 6) Protocol logic (high-level spec before implementation)
This section is your “engineering spec” that you implement against. Keep it precise but not code-heavy.

### 6.1 Sender behavior



**Sender pseudocode (recommended):**


### 6.2 Receiver behavior


**Receiver pseudocode (recommended):**


### 6.3 Error/loss injection spec (if required by phase)
N/A
---

## 7) Experiments + metrics plan (required if phase requires figures/plots)
 

### 7.2 Output artifacts


## 8) Edge cases + test plan

### 8.1 Edge cases you expect

| Edge case | Why it matters | Expected behavior |


### 8.2 Tests you will write because of these edge cases


### 8.3 Test artifacts



## 9) Repo structure + reproducibility





## 10) Team plan, ownership, and milestones
### 10.1 Task ownership
| Task | Owner | Target date | Definition of done |


### 10.2 Milestones (keep it realistic)


