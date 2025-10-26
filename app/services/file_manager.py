from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
VERSIONS_DIR = DATA_DIR / "versions"

for directory in (INPUT_DIR, OUTPUT_DIR, VERSIONS_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def _diagram_json_path(diagram_id: str) -> Path:
    return OUTPUT_DIR / f"{diagram_id}.json"


def _diagram_mermaid_path(diagram_id: str) -> Path:
    return OUTPUT_DIR / f"{diagram_id}.mmd"


def save_uploaded_file(diagram_id: str, filename: str, content: bytes) -> Path:
    input_path = INPUT_DIR / f"{diagram_id}_{filename}"
    input_path.write_bytes(content)
    return input_path


def save_json(diagram_id: str, data: Dict[str, Any]) -> Path:
    path = _diagram_json_path(diagram_id)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_json(diagram_id: str) -> Optional[Dict[str, Any]]:
    path = _diagram_json_path(diagram_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_mermaid(diagram_id: str, mermaid_code: str) -> Path:
    path = _diagram_mermaid_path(diagram_id)
    path.write_text(mermaid_code, encoding="utf-8")
    return path


def load_mermaid(diagram_id: str) -> Optional[str]:
    path = _diagram_mermaid_path(diagram_id)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def save_version(diagram_id: str, data: Dict[str, Any]) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    version_path = VERSIONS_DIR / f"{diagram_id}_{timestamp}.json"
    version_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return version_path


def latest_version(diagram_id: str) -> Optional[Dict[str, Any]]:
    versions = sorted(VERSIONS_DIR.glob(f"{diagram_id}_*.json"))
    if not versions:
        return None
    return json.loads(versions[-1].read_text(encoding="utf-8"))


def list_versions(diagram_id: str) -> list[str]:
    return [path.name for path in sorted(VERSIONS_DIR.glob(f"{diagram_id}_*.json"))]


def input_file_path(diagram_id: str) -> Optional[Path]:
    matches = list(INPUT_DIR.glob(f"{diagram_id}_*"))
    return matches[0] if matches else None
