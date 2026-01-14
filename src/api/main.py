#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastAPI Main Application
"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

app = FastAPI(
    title="Agentic Problem Solver",
    description="Step-by-step problem solving with AI agents",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "agentic-problem-solver"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Agentic Problem Solver",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "solve": "/api/solve (WebSocket)",
            "status": "/api/status",
        },
        "description": "Upload problems and get step-by-step AI solutions"
    }


# Include routers
# Include routers
from src.api.routers.solve import router as solve_router
from src.api.routers.upload import router as upload_router
from src.api.routers.history import router as history_router

app.include_router(solve_router, prefix="/api", tags=["problem-solving"])
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(history_router, prefix="/api", tags=["history"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
