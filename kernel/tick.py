from __future__ import annotations

from time import monotonic_ns
from typing import Any, Dict

from .context import KernelContext, GovernorMode
from .invariants import check_invariants
from ..engine.evaluate import evaluate
from ..engine.enforce import enforce_proposal


def tick_once(ctx: KernelContext, external_inputs: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Deterministic tick:
    - measure duration
    - evaluate proposal
    - enforce invariants
    - update world
    - append audit entry
    """
    external_inputs = external_inputs or {}

    start_ns = monotonic_ns()
    # Pre-invariant check (e.g., stale sensors, etc.) could go here

    proposal = evaluate(ctx.world, ctx.policy, ctx.mode, external_inputs)
    decision = enforce_proposal(ctx, proposal)

    end_ns = monotonic_ns()
    duration_ns = end_ns - start_ns

    ctx.world.tick_index += 1
    ctx.world.last_decision = decision
    ctx.world.vehicle.last_action = decision["action"]
    ctx.world.vehicle.last_justification = decision.get("justification")

    # Invariant check after decision
    violations = check_invariants(ctx.world, ctx.policy, ctx.invariants)

    if duration_ns > ctx.invariants.max_tick_ns:
        violations.append("tick_overrun")
        ctx.world.log_event("tick_overrun", {"duration_ns": duration_ns})

    if violations:
        ctx.world.log_event("invariant_violation", {"violations": violations})
        decision["violations"] = violations

    # Append to audit
    ctx.audit.append(
        event_type="tick",
        payload={
            "tick_index": ctx.world.tick_index,
            "duration_ns": duration_ns,
            "decision": decision,
            "world_snapshot": ctx.world.to_dict(),
        },
    )

    decision["tick_index"] = ctx.world.tick_index
    decision["duration_ns"] = duration_ns
    decision["audit_root"] = ctx.audit.current_root()
    return decision
