# 🌐 Distributed Consensus Simulator

An interactive desktop simulator that demonstrates how distributed nodes
reach **agreement** in a distributed system using a simplified
**Raft-style consensus** mechanism — including leader election, proposal
broadcasting, voting, majority consensus, node failure and recovery.

Built with **Python 3** and **CustomTkinter** for a modern, professional
dashboard-style GUI. No web framework, no database — just clean,
object-oriented, beginner-friendly Python.

---

## ✨ Features

- **Interactive node cluster** — start with 5 nodes, add or remove nodes dynamically
- **Leader election** — a random active node is promoted to Leader, all others become Followers
- **Proposal broadcasting** — the Leader proposes a value (e.g. `DATA-A`) to the cluster
- **Real-time voting** — watch each node vote YES/NO live in the event log
- **Majority consensus** — consensus is reached when YES votes ≥ majority
- **Node failure simulation** — crash a random node; it can no longer vote, and losing the Leader forces a new election
- **Node recovery** — bring offline nodes back online as Followers
- **Reset simulation** — return to a clean 5-node cluster at any time
- **Live dashboard** — statistic cards, colored node cards and a dark event log

## 🛠️ Technologies Used

| Technology    | Purpose                              |
| ------------- | ------------------------------------ |
| Python 3      | Core programming language            |
| CustomTkinter | Modern desktop GUI (Tkinter wrapper) |
| Tkinter       | Underlying windowing toolkit         |
| OOP           | Clean `Node` / `Network` / `ConsensusManager` design |

## 📁 Project Structure

```
Distributed-Consensus-Simulator/
│
├── main.py            # Application entry point
├── config.py          # Constants: window, states, colors, simulation params
├── node.py            # Node class (state, alive, vote, value)
├── network.py         # Network class (cluster management)
├── consensus.py       # ConsensusManager (Raft-style logic)
├── requirements.txt   # Python dependencies
├── README.md          # This file
│
└── gui/
    ├── __init__.py
    └── dashboard.py   # CustomTkinter dashboard (UI)
```

## 🚀 Installation

1. **Clone or download** this repository.
2. Open a terminal in the project folder.
3. Install the dependency:

```bash
pip install -r requirements.txt
```

## ▶️ How to Run

```bash
python main.py
```

## 🧠 How Consensus Works

### 1. Leader Election
Every node starts as a **Follower**. When you press **Elect Leader**, one
random *active* node is promoted to **Leader** and every other active node
stays/becomes a Follower. Raft uses the same idea: one node coordinates,
the rest follow. If the Leader fails, a new election can be held.

### 2. Proposal
You type a value (e.g. `DATA-A`) and press **Start Consensus**. Only the
Leader may broadcast a proposal to the cluster.

### 3. Voting
Each **active** node casts a vote (`YES` or `NO`). Offline nodes cannot
vote. In this simplified model a node votes YES with a probability of
`0.8` (configurable in `config.py` via `VOTE_YES_PROBABILITY`), which
simulates followers that usually agree but may occasionally reject a
proposal — so you can observe both success and failure rounds.

### 4. Majority Calculation
The majority is computed from the **active** nodes:

```
majority = (active_nodes // 2) + 1
```

Examples:

| Active nodes | Majority |
| ------------ | -------- |
| 5            | 3        |
| 4            | 3        |
| 3            | 2        |
| 2            | 2        |
| 1            | 1        |

### 5. Consensus Result
- **YES votes ≥ majority** → `CONSENSUS REACHED` — the value is committed
  to every active node.
- **YES votes < majority** → `CONSENSUS FAILED` — no value is committed.

## 🎬 Example Simulation

```
[08:30:10] System initialized with 5 nodes.
[08:30:20] Node 3 elected as Leader.
[08:30:30] Leader proposed: DATA-A
[08:30:30] Majority required: 3 of 5 active nodes.
[08:30:31] Node 3 voted YES.
[08:30:31] Node 1 voted YES.
[08:30:32] Node 2 voted NO.
[08:30:32] Node 4 voted YES.
[08:30:33] Node 5 voted YES.
[08:30:33] Consensus reached. Value committed to all active nodes.
[08:30:40] Node 4 failed.
[08:30:45] Node 4 recovered.
```

## 📖 Key Concepts (quick theory)

- **Distributed system** — a collection of independent computers (nodes)
  that work together and appear as a single coherent system.
- **Consensus** — the process of getting multiple nodes to agree on a
  single value (e.g. the next entry in a shared log).
- **Leader election** — choosing one node to coordinate, so decisions are
  consistent (Raft elects one leader per *term*).
- **Majority (quorum) voting** — a value is accepted only if more than
  half of the active nodes agree, guaranteeing safety even if some nodes
  fail.
- **Node failure** — a node may crash at any time; it stops voting and
  storing data until it recovers.
- **Node recovery** — a recovered node rejoins as a Follower and can
  participate in later rounds.
- **Raft-style consensus** — a real-world protocol (used by etcd,
  Consul, Kubernetes) that separates consensus into leader election,
  log replication (proposals/votes) and safety. This simulator is a
  simplified teaching version of it.

## 🔮 Future Enhancements

- **Log replication view** — show each node's replicated log entries
- **Network partitions** — split the cluster into isolated groups
- **Adjustable vote probability** — slider in the UI instead of `config.py`
- **Terms & timers** — simulate Raft's randomized election timeouts
- **Charts** — plot votes/rounds over time
- **Sound/visual animations** — pulse effects when consensus is reached

---

*College mini project — Distributed Systems.*
