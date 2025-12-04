________________________________________
Nomad 2 — Deterministic Autonomy Governor
Nomad 2 is a deterministic autonomy governance kernel built for transparent, auditable, safety-critical decision making.
It separates policy, world state, and decision logic to guarantee explainable, reproducible autonomous behavior across any stack or domain.
No machine learning.
No probabilistic inference.
No opaque behavior.
Just deterministic logic, strict envelopes, human-in-the-loop gating, and tamper-evident audits.
________________________________________
🔥 Key Features
Deterministic Decision Engine
•	Pure function decision logic: (world, policy, mode) → proposal
•	Fully explainable justification chains
•	Reproducible ticks with monotonic timing
Safety Invariant Kernel
•	Hard envelopes for LIVE mode
•	Drift/stability constraints
•	Tick-duration bounds with overrun alarms
•	Pre/post decision enforcement
Human-Gated Authority
•	Automatic escalation when nearing safety boundaries
•	Override endpoints for supervisor approval
•	Logged as first-class audit events
Policy-Attested Operation
•	YAML-defined envelopes
•	Mode-scoped policies (shadow / training / live)
•	Policy hash verification at startup
•	Signing-ready structure
Tamper-Evident Audit Chain
•	Hash-linked audit entries
•	Forward-secure log structure
•	Root hash exposed via API for verification
Deterministic World Model
•	Replayable trajectories
•	State, decision, and event history
•	Runs stored in structured, reproducible directories
Optional REST Interface
•	/state – view world state
•	/tick – advance deterministic timestep
•	/decision – last action + justification
•	/override – approve/deny escalations
•	/policy – active policy + hash
________________________________________
📁 Repository Overview
nomad2/
├── app.py                     # Entrypoint
├── configs/                   # Config + policies
├── nomad2/
│   ├── kernel/                # Deterministic core
│   ├── engine/                # Decision logic
│   └── interfaces/            # REST API + adapters
└── runs/                      # Audit logs + world history
________________________________________
🚀 Quick Start
1. Install dependencies
pip install -r requirements.txt
2. Set environment variables
export NOMAD_CONFIG=configs/nomad.yaml
export GOVERNOR_MODE=shadow   # shadow | training | live
3. Run Nomad 2
python app.py
Server starts at:
http://localhost:8080
________________________________________
🧠 Modes
Mode	Behavior
shadow	No actuation; simulate decisions only
training	Unsafe proposals allowed; still bounded by envelopes
live	Strict invariants; hard safety enforcement
________________________________________
🎯 Philosophy
Determinism — Predictable, reconstructable, reasoned autonomy.
Human authority — Supervisors can override any decision.
Traceability — No black boxes; every action is justified and logged.
Explicit boundaries — Safety envelopes are first-class, not afterthoughts.
Nomad 2 demonstrates how autonomy can be governed responsibly, transparently, and certifiably—without relying on opaque ML systems.
________________________________________
📄 License
MIT 
________________________________________
