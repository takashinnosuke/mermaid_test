from __future__ import annotations

from typing import Dict, List, Tuple


def low_confidence_items(diagram: Dict, threshold: float = 0.85) -> List[Tuple[str, float]]:
    confidence_map = diagram.get("confidence", {})
    items = [
        (node.get("id"), float(confidence_map.get(node.get("id"), 0.0)))
        for node in diagram.get("nodes", [])
    ]
    return sorted(
        [(node_id, score) for node_id, score in items if score <= threshold],
        key=lambda item: item[1],
    )


def sorted_confidence(diagram: Dict) -> List[Tuple[str, float]]:
    confidence_map = diagram.get("confidence", {})
    nodes = [
        (node.get("id"), float(confidence_map.get(node.get("id"), 0.0)))
        for node in diagram.get("nodes", [])
    ]
    return sorted(nodes, key=lambda item: item[1])
