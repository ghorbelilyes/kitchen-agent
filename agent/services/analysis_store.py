"""
Simple JSON file-based storage for analysis results.
Each analysis is saved as a JSON file in the 'analyses' directory.
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger

STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "analyses")


def _ensure_store_dir():
    os.makedirs(STORE_DIR, exist_ok=True)


def save_analysis(
    filename: str,
    analysis_data: Dict[str, Any],
    image_filename: Optional[str] = None,
) -> Dict[str, Any]:
    """Save an analysis result and return the stored record."""
    _ensure_store_dir()

    analysis_id = uuid.uuid4().hex[:12]
    record = {
        "id": analysis_id,
        "filename": filename,
        "analyzed_at": datetime.now().isoformat(),
        "analysis": analysis_data,
    }
    if image_filename:
        record["image_filename"] = image_filename

    filepath = os.path.join(STORE_DIR, f"{analysis_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    logger.info(f"Analysis saved: {analysis_id} -> {filename}")
    return record


def list_analyses() -> List[Dict[str, Any]]:
    """Return a list of all saved analyses (summary only, no full data)."""
    _ensure_store_dir()

    results = []
    for fname in os.listdir(STORE_DIR):
        if not fname.endswith(".json"):
            continue
        filepath = os.path.join(STORE_DIR, fname)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                record = json.load(f)
            results.append({
                "id": record["id"],
                "filename": record["filename"],
                "image_filename": record.get("image_filename"),
                "analyzed_at": record["analyzed_at"],
                "dimensions_count": len(record.get("analysis", {}).get("dimensions", [])),
                "risks_count": len(record.get("analysis", {}).get("risky_areas", [])),
                "layout_type": record.get("analysis", {}).get("layout_type", "Unknown"),
            })
        except Exception as e:
            logger.warning(f"Skipping corrupt file {fname}: {e}")
    
    # Sort by date descending (newest first)
    results.sort(key=lambda x: x["analyzed_at"], reverse=True)
    return results


def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Return the full analysis record by ID."""
    _ensure_store_dir()
    filepath = os.path.join(STORE_DIR, f"{analysis_id}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_analysis(analysis_id: str) -> bool:
    """Delete an analysis by ID. Returns True if deleted."""
    _ensure_store_dir()
    filepath = os.path.join(STORE_DIR, f"{analysis_id}.json")
    if not os.path.exists(filepath):
        return False
    os.remove(filepath)
    logger.info(f"Analysis deleted: {analysis_id}")
    return True
