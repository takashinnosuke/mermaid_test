from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from app.services import confidence_filter, file_manager, mermaid_generator

router = APIRouter()


class NodeUpdate(BaseModel):
    diagram_id: str
    node_id: str
    label: Optional[str] = None
    confidence: Optional[float] = None


class EdgeUpdate(BaseModel):
    diagram_id: str
    from_id: str
    to_id: str
    relation: Optional[str] = None


class JsonUpdate(BaseModel):
    diagram_id: str
    payload: Dict[str, Any]


@router.get("/review/{diagram_id}", response_class=HTMLResponse)
async def review_page(diagram_id: str, request: Request) -> HTMLResponse:
    diagram = file_manager.load_json(diagram_id)
    if diagram is None:
        raise HTTPException(status_code=404, detail="Diagram not found")

    mermaid_code = file_manager.load_mermaid(diagram_id) or mermaid_generator.generate_mermaid(diagram)
    low_confidence = confidence_filter.low_confidence_items(diagram)
    confidence_rank = confidence_filter.sorted_confidence(diagram)
    versions = file_manager.list_versions(diagram_id)

    return request.app.state.templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "diagram_id": diagram_id,
            "diagram_json": json.dumps(diagram, ensure_ascii=False, indent=2),
            "mermaid_code": mermaid_code,
            "low_confidence": low_confidence,
            "confidence_rank": confidence_rank,
            "versions": versions,
        },
    )


@router.put("/update_node")
async def update_node(update: NodeUpdate) -> JSONResponse:
    diagram = file_manager.load_json(update.diagram_id)
    if diagram is None:
        raise HTTPException(status_code=404, detail="Diagram not found")

    updated = False
    for node in diagram.get("nodes", []):
        if node.get("id") == update.node_id:
            if update.label is not None:
                node["label"] = update.label
            updated = True
            break

    if update.confidence is not None:
        diagram.setdefault("confidence", {})[update.node_id] = update.confidence
        updated = True

    if not updated:
        raise HTTPException(status_code=404, detail="Node not found")

    file_manager.save_json(update.diagram_id, diagram)
    mermaid_code = mermaid_generator.generate_mermaid(diagram)
    file_manager.save_mermaid(update.diagram_id, mermaid_code)
    return JSONResponse({"status": "ok", "mermaid": mermaid_code, "diagram": diagram})


@router.put("/update_edge")
async def update_edge(update: EdgeUpdate) -> JSONResponse:
    diagram = file_manager.load_json(update.diagram_id)
    if diagram is None:
        raise HTTPException(status_code=404, detail="Diagram not found")

    updated = False
    for edge in diagram.get("edges", []):
        if edge.get("from") == update.from_id and edge.get("to") == update.to_id:
            if update.relation is not None:
                edge["relation"] = update.relation
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Edge not found")

    file_manager.save_json(update.diagram_id, diagram)
    mermaid_code = mermaid_generator.generate_mermaid(diagram)
    file_manager.save_mermaid(update.diagram_id, mermaid_code)
    return JSONResponse({"status": "ok", "mermaid": mermaid_code, "diagram": diagram})


@router.put("/update_json")
async def update_json(update: JsonUpdate) -> JSONResponse:
    file_manager.save_json(update.diagram_id, update.payload)
    mermaid_code = mermaid_generator.generate_mermaid(update.payload)
    file_manager.save_mermaid(update.diagram_id, mermaid_code)
    return JSONResponse({"status": "ok", "mermaid": mermaid_code})


@router.post("/approve/{diagram_id}")
async def approve_diagram(diagram_id: str) -> JSONResponse:
    diagram = file_manager.load_json(diagram_id)
    if diagram is None:
        raise HTTPException(status_code=404, detail="Diagram not found")

    version_path = file_manager.save_version(diagram_id, diagram)
    return JSONResponse({"status": "ok", "version": version_path.name})
