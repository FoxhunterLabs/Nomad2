from __future__ import annotations

from flask import Blueprint, jsonify, request

from nomad2.kernel.context import KernelContext
from nomad2.kernel.tick import tick_once
from nomad2.engine.escalations import apply_override


def create_api_blueprint(ctx: KernelContext) -> Blueprint:
    bp = Blueprint("api", __name__)

    @bp.get("/health")
    def health() -> tuple:
        return jsonify(
            {
                "status": "ok",
                "mode": ctx.mode.value,
                "policy_id": ctx.policy.id,
                "policy_hash": ctx.policy.policy_hash,
                "audit_root": ctx.audit.current_root(),
            }
        ), 200

    @bp.get("/state")
    def state() -> tuple:
        return jsonify(
            {
                "mode": ctx.mode.value,
                "world": ctx.world.to_dict(),
                "policy_id": ctx.policy.id,
            }
        ), 200

    @bp.post("/tick")
    def tick() -> tuple:
        external_inputs = request.get_json(silent=True) or {}
        decision = tick_once(ctx, external_inputs)
        return jsonify(decision), 200

    @bp.get("/decision")
    def last_decision() -> tuple:
        if ctx.world.last_decision is None:
            return jsonify({"error": "no decisions yet"}), 404
        return jsonify(ctx.world.last_decision), 200

    @bp.post("/override")
    def override() -> tuple:
        payload = request.get_json(silent=True) or {}
        result = apply_override(ctx, payload)
        return jsonify(result), 200

    @bp.get("/policy")
    def policy() -> tuple:
        return jsonify(
            {
                "metadata": ctx.policy.metadata.model_dump(),
                "envelope": ctx.policy.envelope,
                "actions": ctx.policy.actions,
                "escalation": ctx.policy.escalation,
                "policy_hash": ctx.policy.policy_hash,
            }
        ), 200

    return bp
