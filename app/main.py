"""
FastAPI application entry point
"""
from fastapi import FastAPI
from app.models.base import Base, engine
from app.api import cases  # Import router

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Caseflow Chat API",
    description="Immigration case intake system with AI",
    version="1.0.0"
)
app.include_router(cases.router)


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "Caseflow Chat API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """Detailed health check"""
    return {"status": "healthy"}