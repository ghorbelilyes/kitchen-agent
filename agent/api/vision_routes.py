from fastapi import APIRouter, UploadFile, File, HTTPException
from loguru import logger
from services.vision_analyzer import extract_plan_dimensions
from typing import Dict, Any

router = APIRouter()

@router.post("/analyze-plan")
async def analyze_plan(file: UploadFile = File(...)) -> Dict[str, Any]:
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
        raise HTTPException(status_code=400, detail="Invalid file format. Only JPG, PNG, or PDF.")

    logger.info(f"Received kitchen plan: {file.filename}")
    file_bytes = await file.read()
    
    extracted_data = await extract_plan_dimensions(file_bytes, file.filename)
    return extracted_data
