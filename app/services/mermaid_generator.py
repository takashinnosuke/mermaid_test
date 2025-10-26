from __future__ import annotations

from typing import Dict, List


def generate_mermaid(json_data: Dict) -> str:
    """Convert diagram JSON data into a Mermaid graph string."""
    title = json_data.get("title")
    lines: List[str] = ["graph TD"]

    if title:
        lines.insert(0, f"%% {title}")

    for node in json_data.get("nodes", []):
        node_id = node.get("id", "").strip() or "unknown"
        label = node.get("label", "").strip() or node_id
        lines.append(f"    {node_id}[{label}]")

    for edge in json_data.get("edges", []):
        origin = edge.get("from", "").strip() or "unknown"
        target = edge.get("to", "").strip() or "unknown"
        relation = edge.get("relation", "").strip()
        relation_segment = f"|{relation}| " if relation else ""
        lines.append(f"    {origin} -->{relation_segment}{target}")

    return "\n".join(lines)
