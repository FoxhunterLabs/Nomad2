from __future__ import annotations

from typing import Dict, Any

from nomad2.kernel.world import World
from nomad2.kernel.policy import PolicyEnvelope
from nomad2.kernel.context import GovernorMode


def evaluate(
    world: World,
    policy: PolicyEnvelope,
    mode: GovernorMode,
    external_inputs: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Pure function: (world, policy, mode, external_inputs) -> proposal.
    No randomness, no side effects.
    """
    drift = world.vehicle.drift
    stability = world.vehicle.stability

    # Simple deterministic rule-based action selection
    actions = policy.actions

    chosen_action = "stop_safe"
    reason_chain = []

    # Normal
    normal = actions.get("normal")
    if normal:
        if drift <= normal["drift_max"] and stability >= normal["stability_min"]:
            chosen_action = "normal"
            reason_chain.append(
                {
                    "rule": "normal_envelope",
                    "drift": drift,
                    "stability": stability,
                    "thresholds": normal,
                }
            )

    # Cautious
    if chosen_action == "stop_safe":
        cautious = actions.get("cautious")
        if cautious:
            if drift <= cautious["drift_max"] and stability >= cautious["stability_min"]:
                chosen_action = "cautious"
                reason_chain.append(
                    {
                        "rule": "cautious_envelope",
                        "drift": drift,
                        "stability": stability,
                        "thresholds": cautious,
                    }
                )

    # Fallback stop_safe
    if chosen_action == "stop_safe":
        stop_safe = actions.get("stop_safe", {})
        reason_chain.append(
            {
                "rule": "fallback_stop_safe",
                "drift": drift,
                "stability": stability,
                "thresholds": stop_safe,
            }
        )

    # Human gate if near boundary (example heuristic)
    requires_human_gate = False
    if mode == GovernorMode.LIVE:
        live_env = policy.envelope
        stability_min_live = live_env.get("stability_min_live", 50)
        guard_band = 5.0
        if stability < stability_min_live + guard_band:
            requires_human_gate = True
            reason_chain.append(
                {
                    "rule": "near_live_stability_boundary",
                    "stability": stability,
                    "stability_min_live": stability_min_live,
                    "guard_band": guard_band,
                }
            )

    proposal = {
        "action": chosen_action,
        "justification": reason_chain,
        "requires_human_gate": requires_human_gate,
    }
    return proposal
