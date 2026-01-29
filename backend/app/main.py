import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.data.slides import SLIDES
from app.models import Slide


settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("Starting AI Voice Presentation Server...")
    logger.info(f"Loaded {len(SLIDES)} slides")
    yield
    logger.info("Shutting down AI Voice Presentation Server...")



app = FastAPI(
    title="AI Voice Presentation",
    description="Real-time AI voice presentation with OpenAI Realtime API",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/slides", response_model=list[Slide])
async def get_slides() -> list[Slide]:
    """Get all presentation slides."""
    return SLIDES


@app.get("/api/slides/{slide_id}", response_model=Slide)
async def get_slide(slide_id: int) -> Slide:
    """Get a specific slide by ID."""
    for slide in SLIDES:
        if slide.id == slide_id:
            return slide
    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail=f"Slide {slide_id} not found")



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
