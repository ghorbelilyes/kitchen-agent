from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from loguru import logger
from services.vision_analyzer import extract_plan_dimensions, list_available_pi_models
from services.analysis_store import save_analysis, list_analyses, get_analysis, delete_analysis
from typing import Dict, Any, List

router = APIRouter()


@router.post("/analyze-plan")
async def analyze_plan(
    file: UploadFile = File(...),
    model: str | None = Form(default=None),
    stored_filename: str | None = Form(default=None),
) -> Dict[str, Any]:
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
        raise HTTPException(status_code=400, detail="Invalid file format. Only JPG, PNG, or PDF.")

    logger.info(f"Received kitchen plan: {file.filename}")
    file_bytes = await file.read()
    selected_model = model.strip() if model and model.strip() else None

    extracted_data = await extract_plan_dimensions(file_bytes, file.filename, selected_model)

    if selected_model and "error" not in extracted_data:
        extracted_data["_selected_model"] = selected_model

    # Save the analysis if successful (no error key in result)
    if "error" not in extracted_data:
        record = save_analysis(
            file.filename,
            extracted_data,
            image_filename=stored_filename,
        )
        extracted_data["_analysis_id"] = record["id"]
        extracted_data["_analyzed_at"] = record["analyzed_at"]
        if record.get("image_filename"):
            extracted_data["_image_filename"] = record["image_filename"]

    return extracted_data


@router.get("/models")
async def get_available_models() -> Dict[str, Any]:
    """List Pi models available in the local /model selector."""
    try:
        return await list_available_pi_models()
    except Exception as exc:
        logger.error(f"Failed to load Pi models: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/analyses")
async def get_all_analyses() -> List[Dict[str, Any]]:
    """List all saved analyses (summary only)."""
    return list_analyses()


@router.get("/analyses/{analysis_id}")
async def get_analysis_detail(analysis_id: str) -> Dict[str, Any]:
    """Get full analysis details by ID."""
    record = get_analysis(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return record


@router.delete("/analyses/{analysis_id}")
async def delete_analysis_record(analysis_id: str) -> Dict[str, Any]:
    """Delete an analysis by ID."""
    deleted = delete_analysis(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return {"message": "Analysis deleted successfully", "id": analysis_id}
