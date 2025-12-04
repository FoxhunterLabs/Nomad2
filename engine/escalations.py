from __future__ import annotations

from typing import Dict, Any

from nomad2.kernel.context import KernelContext


def apply_override(ctx: KernelContext, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Approve/deny a human-gate proposal.
    This is a placeholder; in a real system, you'd look up pending gates,
    roles, dual approvals, etc.
    """
    decision = payload.get("decision")
    approved = bool(payload.get("approved", False))
    reason = payload.get("reason", "")

    ctx.world.log_event(
        "human_gate_override",
        {"decision": decision, "approved": approved, "reason": reason},
    )

    ctx.audit.append(
        "human_gate_override",
        {"decision": decision, "approved": approved, "reason": reason},
    )

    result = {
        "override_applied": approved,
        "decision": decision,
        "reason": reason,
    }
    return result
