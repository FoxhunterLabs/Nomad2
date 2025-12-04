from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional


@dataclass
class AuditLog:
    log_dir: Path
    log_file: Path
    last_hash: str = "0" * 64

    @classmethod
    def create(cls, base_dir: str) -> "AuditLog":
        log_dir = Path(base_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "audit.jsonl"

        last_hash = "0" * 64
        if log_file.exists():
            # Rebuild last_hash from existing file deterministically
            with log_file.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        last_hash = entry.get("hash", last_hash)
                    except json.JSONDecodeError:
                        continue

        return cls(log_dir=log_dir, log_file=log_file, last_hash=last_hash)

    def append(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        entry = {
            "prev_hash": self.last_hash,
            "event_type": event_type,
            "payload": payload,
        }
        h = hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()
        entry["hash"] = h
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        self.last_hash = h
        return entry

    def current_root(self) -> str:
        return self.last_hash
