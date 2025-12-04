from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Any, List

import yaml
from pydantic import BaseModel, Field, ValidationError


class PolicyMetadata(BaseModel):
    id: str
    version: str
    author: str
    created_at: str
    scope: str
    mode_allow: List[str]


class PolicyEnvelope(BaseModel):
    metadata: PolicyMetadata
    signing: Dict[str, Any]
    envelope: Dict[str, Any]
    actions: Dict[str, Dict[str, Any]]
    escalation: Dict[str, Any]
    policy_hash: str = Field(...)

    @property
    def id(self) -> str:
        return self.metadata.id


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def load_policy(path: str, mode: str) -> PolicyEnvelope:
    policy_path = Path(path)
    if not policy_path.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")

    policy_hash = _hash_file(policy_path)
    raw = yaml.safe_load(policy_path.read_text(encoding="utf-8"))

    try:
        metadata = PolicyMetadata(**raw["metadata"])
    except ValidationError as e:
        raise ValueError(f"Invalid policy metadata: {e}") from e

    if mode not in metadata.mode_allow:
        raise ValueError(
            f"Policy {metadata.id} does not allow mode '{mode}'. "
            f"Allowed modes: {metadata.mode_allow}"
        )

    envelope = PolicyEnvelope(
        metadata=metadata,
        signing=raw.get("signing", {}),
        envelope=raw.get("envelope", {}),
        actions=raw.get("actions", {}),
        escalation=raw.get("escalation", {}),
        policy_hash=policy_hash,
    )
    return envelope
