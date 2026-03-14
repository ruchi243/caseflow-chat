"""
FastAPI application entry point
"""
from fastapi import FastAPI
from app.models import base
from app.api import cases, documents, agent # Add documents

# Create tables on startup
base.Base.metadata.create_all(bind=base.engine)


app = FastAPI(
    title="Caseflow Chat API",
    description="Immigration case intake system with AI",
    version="1.0.0"
)

app.include_router(agent.router)

# Include routers
app.include_router(cases.router)
app.include_router(documents.router)  # Add this


@app.get("/")
def root():
    return {
        "message": "Caseflow Chat API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}