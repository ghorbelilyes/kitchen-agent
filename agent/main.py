import sys

if sys.version_info < (3, 10):
    raise RuntimeError("Kitchen Vision Agent requires Python 3.10 or higher.")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn
from api.vision_routes import router as vision_router

app = FastAPI(title="Kitchen Vision Agent")

# Allow requests from the Java backend and plain Phase 3 frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vision_router, prefix="/api/vision", tags=["vision"])

@app.on_event("startup")
async def startup_event():
    logger.info("Kitchen Vision Agent started.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
