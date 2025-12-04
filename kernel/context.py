from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any

from .world import World
from .policy import PolicyEnvelope
from .audit import AuditLog
from .invariants import InvariantSet


class GovernorMode(str, Enum):
    SHADOW = "shadow"
    TRAINING = "training"
    LIVE = "live"


@dataclass
class KernelContext:
    """
    Shared kernel context passed into ticks, engine, and API.
    """
    mode: GovernorMode
    world: World
    policy: PolicyEnvelope
    invariants: InvariantSet
    audit: AuditLog
    config: Dict[str, Any]
