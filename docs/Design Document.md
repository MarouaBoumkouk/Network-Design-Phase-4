## Network Design Project - Phase Proposal and Design Document (Phase 2 of 5)
**Purpose:**  
** Names: ** Maroua Boumkouk Matthew Nguyen   
**GitHub Repo URL (with GitHub usernames):**  https://github.com/MattN11/Network-Design-Phase-2
**Phase:** 2  
**Submission Date:** Friday 09 Octobre 2026 
**Version:** (1)

## 0 Executive Summary 
   For Phase 2, our team will build off of our previous UDP transfer file project but implementing the Reliable Data Transfer 2.2 Protocol. 


## 1) Phase requirements
### 1.1 Demo deliverable
- **Private YouTube link:**  


### 1.2 Required demo scenarios

### 1.3 Required figures / plots
N/A
---

## 2) Phase plan (company-style, lightweight)


### 2.1 Scope: what changes/additions this phase

- **Out of scope (explicitly):** handling lost or corrupted packets, retransmission, checksums

### 2.2 Acceptance criteria (your checklist)
List 5–10 measurable checks that mean you’re done (examples below).

- [ ] 
- [ ] All required scenarios demonstrated in the video
- [ ] 
- [ ] 
- [ ] 

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


