from __future__ import annotations

from deepdiff import DeepDiff
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.services import file_manager

router = APIRouter()


@router.get("/diff/{diagram_id}")
async def diff_diagram(diagram_id: str) -> JSONResponse:
    current = file_manager.load_json(diagram_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Diagram not found")

    previous = file_manager.latest_version(diagram_id)
    if previous is None:
        return JSONResponse({"status": "ok", "diff": {}, "message": "No previous versions"})

    diff = DeepDiff(previous, current, ignore_order=True).to_dict()
    return JSONResponse({"status": "ok", "diff": diff})
