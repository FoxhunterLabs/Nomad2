from __future__ import annotations

from typing import Dict, Any
from uuid import uuid4

from nomad2.kernel.context import KernelContext, GovernorMode


def enforce_proposal(ctx: KernelContext, proposal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enforce invariants + mode rules on the proposal.
    May:
      - downgrade action
      - require human gate
      - block actuation in shadow mode
    """
    mode = ctx.mode
    action = proposal["action"]
    justification = proposal.get("justification", [])
    requires_human_gate = proposal.get("requires_human_gate", False)

    # Shadow mode: never actuate, only simulate
    if mode == GovernorMode.SHADOW:
        effective_action = "none"
        justification.append(
            {"rule": "shadow_mode", "note": "no actuation; proposals are simulated only"}
        )
    else:
        effective_action = action

    # Human-gated actions
    human_gate_id = None
    if requires_human_gate:
        human_gate_id = str(uuid4())
        ctx.world.pending_human_gate = ctx.world.pending_human_gate or None
        ctx.world.pending_human_gate = None
        ctx.world.pending_human_gate = type(ctx.world).pending_human_gate.__class__ if False else None  # type: ignore

        # Simpler: store gate as dict on world.events
        ctx.world.log_event(
            "human_gate_requested",
            {
                "human_gate_id": human_gate_id,
                "proposal": {"action": action, "justification": justification},
            },
        )

    decision = {
        "action": effective_action,
        "proposed_action": action,
        "justification": justification,
        "requires_human_gate": requires_human_gate,
        "human_gate_id": human_gate_id,
        "mode": mode.value,
    }
    return decision
