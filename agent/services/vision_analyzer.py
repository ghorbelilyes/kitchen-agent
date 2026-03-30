from loguru import logger
from typing import Dict, Any
import asyncio

async def extract_plan_dimensions(image_bytes: bytes, filename: str) -> Dict[str, Any]:
    logger.info(f"Analyzing {filename} with STUBBED Vision Model...")
    
    # Simulate API Latency to make the UI feel real
    await asyncio.sleep(1.5)
    
    # STUBBED RETURN that triggers our validation logic well
    return {
        "layout_type": "L-Shape with Island",
        "visible_elements": ["Sink", "Island", "Tall Oven Unit"],
        "dimensions": [
            {
                "id": "wall_A",
                "label": "Total Wall Length A",
                "expectedValue": 3200,
                "unit": "mm",
                "isUnreadable": False
            },
            {
                "id": "wall_B",
                "label": "Total Wall Length B",
                "expectedValue": 2500,
                "unit": "mm",
                "isUnreadable": False
            },
            {
                "id": "window_sill",
                "label": "Window Sill Height",
                "expectedValue": None,
                "unit": "mm",
                "isUnreadable": True # Triggers 'UNREADABLE' logic
            }
        ],
        "risky_areas": [
            "Sink plumbing point not clearly marked.",
            "Island clearance near door seems < 900mm."
        ]
    }
