"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from backend.api.routes import router
from backend.config import settings
from backend.utils.logger import log

# Create FastAPI app
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="A complete RAG system with document upload, web scraping, and question answering capabilities using Llama 3"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["RAG System"])

# Serve static files (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
async def root():
    """Serve the frontend."""
    frontend_file = frontend_path / "index.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    return {"message": "RAG System API", "version": settings.app.version}


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    log.info(f"Starting {settings.app.name} v{settings.app.version}")
    log.info(f"Server running on {settings.app.host}:{settings.app.port}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    log.info("Shutting down RAG System")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )
