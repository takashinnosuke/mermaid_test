from __future__ import annotations

import base64
import os
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel
from starlette.background import BackgroundTasks

from app.services import file_manager, mermaid_generator

router = APIRouter()


class UploadResponse(BaseModel):
    diagram_id: str
    filename: str
    saved_path: str


class ConvertRequest(BaseModel):
    diagram_id: str
    provider: Optional[str] = None
    prompt: Optional[str] = None


class ConvertResponse(BaseModel):
    diagram_id: str
    json: Dict[str, Any]


class GenerateMermaidRequest(BaseModel):
    diagram_id: str


class GenerateMermaidResponse(BaseModel):
    diagram_id: str
    mermaid: str


@router.post("/upload", response_model=UploadResponse)
async def upload_diagram(file: UploadFile = File(...)) -> UploadResponse:
    diagram_id = str(uuid.uuid4())
    content = await file.read()
    saved_path = file_manager.save_uploaded_file(diagram_id, file.filename, content)
    return UploadResponse(diagram_id=diagram_id, filename=file.filename, saved_path=str(saved_path))


def _call_structure_api(file_path: Path, provider: str, prompt: Optional[str]) -> Dict[str, Any]:
    """Dummy integration with Gemini/ChatGPT style APIs."""
    api_key = None
    headers = {}

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    else:
        provider = "openai"
        api_key = os.getenv("OPENAI_API_KEY")
        endpoint = "https://api.openai.com/v1/responses"

    if not api_key:
        encoded = base64.b64encode(file_path.read_bytes()).decode("utf-8") if file_path.exists() else ""
        return {
            "title": file_path.stem,
            "nodes": [
                {"id": "A", "label": "ダミー開始"},
                {"id": "B", "label": "ダミー終了"},
            ],
            "edges": [
                {"from": "A", "to": "B", "relation": "フロー"},
            ],
            "confidence": {"A": 0.7, "B": 0.6},
            "source_preview": encoded,
            "provider": provider,
            "prompt": prompt,
        }

    headers["Authorization"] = f"Bearer {api_key}"

    payload_prompt = prompt or (
        "You are a diagram structure extractor. Given an image or chart, output its node "
        "and edge relationships in JSON with title, nodes, edges and confidence."
    )

    body = {
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": payload_prompt},
                ],
            }
        ]
    }

    try:
        response = requests.post(endpoint, headers=headers, json=body, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:  # pragma: no cover - network failure fallback
        raise HTTPException(status_code=502, detail=f"API call failed: {exc}")

    return data.get("output", data)


@router.post("/convert", response_model=ConvertResponse)
async def convert_diagram(request: ConvertRequest, background_tasks: BackgroundTasks) -> ConvertResponse:
    file_path = file_manager.input_file_path(request.diagram_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    provider = request.provider or os.getenv("DEFAULT_PROVIDER", "openai")
    result = _call_structure_api(file_path, provider, request.prompt)

    if not result:
        raise HTTPException(status_code=500, detail="Empty response from structure API")

    file_manager.save_json(request.diagram_id, result)

    def _generate_mermaid() -> None:
        mermaid_code = mermaid_generator.generate_mermaid(result)
        file_manager.save_mermaid(request.diagram_id, mermaid_code)

    background_tasks.add_task(_generate_mermaid)

    return ConvertResponse(diagram_id=request.diagram_id, json=result)


@router.post("/generate_mermaid", response_model=GenerateMermaidResponse)
async def generate_mermaid_endpoint(request: GenerateMermaidRequest) -> GenerateMermaidResponse:
    diagram = file_manager.load_json(request.diagram_id)
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram JSON not found")

    mermaid_code = mermaid_generator.generate_mermaid(diagram)
    file_manager.save_mermaid(request.diagram_id, mermaid_code)
    return GenerateMermaidResponse(diagram_id=request.diagram_id, mermaid=mermaid_code)
