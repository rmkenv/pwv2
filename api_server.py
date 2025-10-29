#!/usr/bin/env python3
"""
FastAPI Server for Regulatory Compliance RAG System
REST API for semantic search and AI-powered Q&A
"""

import os
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import query service
try:
    from query_service import QueryService
    QUERY_SERVICE_AVAILABLE = True
except ImportError:
    QUERY_SERVICE_AVAILABLE = False


# Pydantic models
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    use_ai: bool = True


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[dict]
    num_sources: int
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    vector_db_loaded: bool
    total_documents: int
    timestamp: str


# Initialize FastAPI app
app = FastAPI(
    title="Federal Regulatory Compliance API",
    description="Semantic search and AI-powered Q&A for federal regulations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global query service instance
query_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize query service on startup"""
    global query_service

    if not QUERY_SERVICE_AVAILABLE:
        print("⚠ Query service not available")
        return

    try:
        vector_db_path = os.getenv('VECTOR_DB_PATH', 'vector_db/regulatory_vector_db')
        model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

        print(f"Loading query service from {vector_db_path}...")
        query_service = QueryService(
            vector_db_path=vector_db_path,
            model_name=model_name
        )
        print("✓ Query service ready")

    except Exception as e:
        print(f"✗ Failed to load query service: {e}")


@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint"""
    return {
        "message": "Federal Regulatory Compliance API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "query": "/query (POST)",
            "search": "/search (POST)"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    if query_service and query_service.vector_db:
        return HealthResponse(
            status="healthy",
            vector_db_loaded=True,
            total_documents=query_service.vector_db.index.ntotal,
            timestamp=datetime.now().isoformat()
        )
    else:
        return HealthResponse(
            status="unhealthy",
            vector_db_loaded=False,
            total_documents=0,
            timestamp=datetime.now().isoformat()
        )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Ask a compliance question

    Returns answer with cited sources
    """
    if not query_service:
        raise HTTPException(status_code=503, detail="Query service not available")

    try:
        result = query_service.ask(
            question=request.question,
            top_k=request.top_k,
            use_ai=request.use_ai
        )

        return QueryResponse(
            question=result['question'],
            answer=result['answer'],
            sources=result['sources'],
            num_sources=result['num_sources'],
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search(request: QueryRequest):
    """
    Semantic search for relevant regulatory content

    Returns matching documents without AI answer generation
    """
    if not query_service:
        raise HTTPException(status_code=503, detail="Query service not available")

    try:
        results = query_service.semantic_search(
            query=request.question,
            top_k=request.top_k
        )

        return {
            "query": request.question,
            "results": results,
            "num_results": len(results),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('PORT', 8000))

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
