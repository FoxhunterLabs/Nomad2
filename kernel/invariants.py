from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .world import World
from .policy import PolicyEnvelope


@dataclass
class InvariantSet:
    max_drift_live: float
    min_stability_live: float
    max_tick_ns: int


def build_invariants(policy: PolicyEnvelope, max_tick_ns: int) -> InvariantSet:
    env = policy.envelope
    return InvariantSet(
        max_drift_live=float(env.get("drift_max_live", 60.0)),
        min_stability_live=float(env.get("stability_min_live", 50.0)),
        max_tick_ns=max_tick_ns,
    )


def check_invariants(world: World, policy: PolicyEnvelope, invariants: InvariantSet) -> List[str]:
    violations: List[str] = []

    if world.mode == "live":
        if world.vehicle.drift > invariants.max_drift_live:
            violations.append("drift_exceeds_live_max")
        if world.vehicle.stability < invariants.min_stability_live:
            violations.append("stability_below_live_min")

    return violations
