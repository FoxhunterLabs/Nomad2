import os
from pathlib import Path
from typing import Any, Dict

import yaml
from flask import Flask

from nomad2.kernel.context import KernelContext, GovernorMode
from nomad2.kernel.world import init_world
from nomad2.kernel.policy import load_policy
from nomad2.kernel.audit import AuditLog
from nomad2.kernel.invariants import build_invariants
from nomad2.interfaces.rest import create_api_blueprint


DEFAULT_CONFIG_PATH = "configs/nomad.yaml"


def load_config(path: str | None) -> Dict[str, Any]:
    cfg_path = Path(path or DEFAULT_CONFIG_PATH)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_mode(env_mode: str | None, cfg: Dict[str, Any]) -> GovernorMode:
    cfg_mode = cfg.get("nomad", {}).get("mode", "shadow").lower()
    raw_mode = (env_mode or cfg_mode).lower()
    if raw_mode not in {"shadow", "training", "live"}:
        raw_mode = "shadow"
    return GovernorMode(raw_mode)


def create_app() -> Flask:
    app = Flask(__name__)

    # 1. Load config
    config_path = os.getenv("NOMAD_CONFIG", DEFAULT_CONFIG_PATH)
    app.config["NOMAD_CONFIG_PATH"] = config_path
    cfg = load_config(config_path)
    app.config["NOMAD_CONFIG"] = cfg

    # 2. Resolve mode
    env_mode = os.getenv("GOVERNOR_MODE")
    mode = resolve_mode(env_mode, cfg)
    app.config["GOVERNOR_MODE"] = mode.value

    # 3. Load policy
    nomad_cfg = cfg.get("nomad", {})
    policy_file = nomad_cfg.get("policy_file", "configs/policies/urban_demo_v2.yaml")
    policy = load_policy(policy_file, mode.value)

    # 4. Init world and audit
    data_dir = nomad_cfg.get("data_dir", "runs")
    world = init_world(data_dir, mode.value)
    audit = AuditLog.create(base_dir=data_dir)

    # 5. Build invariants
    max_tick_ns = int(nomad_cfg.get("max_tick_ns", 50_000_000))
    invariants = build_invariants(policy, max_tick_ns=max_tick_ns)

    # 6. Assemble kernel context
    ctx = KernelContext(
        mode=mode,
        world=world,
        policy=policy,
        invariants=invariants,
        audit=audit,
        config=cfg,
    )

    # 7. Register REST API
    api_bp = create_api_blueprint(ctx)
    app.register_blueprint(api_bp, url_prefix="/")

    return app


if __name__ == "__main__":
    flask_app = create_app()
    cfg = flask_app.config["NOMAD_CONFIG"]["nomad"]
    host = cfg.get("host", "0.0.0.0")
    port = int(cfg.get("port", 8080))

    # For real deployment, run behind gunicorn/uwsgi; debug=False here by default.
    flask_app.run(host=host, port=port, debug=False)
