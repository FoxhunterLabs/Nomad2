from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass
class VehicleState:
    drift: float = 0.0          # e.g. lateral deviation
    stability: float = 100.0    # 0–100
    last_action: Optional[str] = None
    last_justification: Optional[Dict[str, Any]] = None


@dataclass
class HumanGateRequest:
    id: str
    proposal: Dict[str, Any]
    status: str = "pending"     # pending | approved | denied
    reason: Optional[str] = None


@dataclass
class World:
    tick_index: int = 0
    mode: str = "shadow"
    vehicle: VehicleState = field(default_factory=VehicleState)
    pending_human_gate: Optional[HumanGateRequest] = None
    last_decision: Optional[Dict[str, Any]] = None
    events: list[Dict[str, Any]] = field(default_factory=list)
    data_dir: str = "runs"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tick_index": self.tick_index,
            "mode": self.mode,
            "vehicle": asdict(self.vehicle),
            "pending_human_gate": asdict(self.pending_human_gate) if self.pending_human_gate else None,
            "last_decision": self.last_decision,
            "events": self.events[-50:],  # keep recent in API
        }

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        self.events.append({"type": event_type, "payload": payload, "tick": self.tick_index})


def init_world(data_dir: str, mode: str) -> World:
    os.makedirs(data_dir, exist_ok=True)
    world = World(mode=mode, data_dir=data_dir)
    world.log_event("world_initialized", {"mode": mode})
    return world
