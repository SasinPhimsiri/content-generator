"""FastAPI main application for Jenosize Content Generator."""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any
import time

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

from .models import ContentRequest, ContentResponse, HealthResponse
from ..agents.coordinator import content_coordinator
from ..core.data_pipeline import data_processor, content_validator
from ..core.ollama_client import ollama_client
from ..core.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Jenosize Content Generator API")
    
    model_available = await ollama_client.check_model_availability()
    if not model_available:
        logger.warning(f"Model {ollama_client.model} not available, attempting to pull...")
        pull_success = await ollama_client.pull_model()
        if not pull_success:
            logger.error("Failed to pull model, some features may not work")
    
    yield
    
    logger.info("Shutting down Jenosize Content Generator API")


app = FastAPI(
    title="Jenosize Content Generator API",
    description="Multi-agent content generation system for business articles",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    model_available = await ollama_client.check_model_availability()
    
    return HealthResponse(
        status="healthy" if model_available else "degraded",
        timestamp=int(time.time()),
        version="1.0.0",
        model_available=model_available,
        model_name=ollama_client.model
    )


@app.post("/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    background_tasks: BackgroundTasks
):
    """Generate content using the multi-agent system."""
    try:
        logger.info(f"Received content generation request for topic: {request.topic}")
        
        # Process input data
        processed_input = await data_processor.process_input(request.dict())
        
        # Generate content using coordinator
        generation_result = await content_coordinator.generate_content(processed_input)
        
        # Validate generated content
        validation_result = content_validator.validate_content(
            content=generation_result["final_content"],
            metadata=generation_result["content_metadata"]
        )
        
        # Log generation metrics in background
        background_tasks.add_task(
            log_generation_metrics,
            request.topic,
            generation_result,
            validation_result
        )
        
        return ContentResponse(
            content=generation_result["final_content"],
            metadata=generation_result["content_metadata"],
            quality_score=generation_result["quality_score"],
            workflow_data=generation_result["workflow_data"],
            generation_metadata=generation_result["generation_metadata"],
            validation_result=validation_result,
            excel_export_path=generation_result.get("excel_export_path")
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during content generation")


@app.post("/generate-fast", response_model=ContentResponse)
async def generate_content_fast(
    request: ContentRequest,
    background_tasks: BackgroundTasks
):
    """Generate content quickly using simplified workflow (faster but less thorough)."""
    try:
        logger.info(f"Received fast content generation request for topic: {request.topic}")
        
        # Process input data
        processed_input = await data_processor.process_input(request.dict())
        
        # Generate content using fast coordinator
        generation_result = await content_coordinator.generate_content(processed_input)
        
        # Validate generated content
        validation_result = content_validator.validate_content(
            content=generation_result["final_content"],
            metadata=generation_result["content_metadata"]
        )
        
        # Log generation metrics in background
        background_tasks.add_task(
            log_generation_metrics,
            request.topic,
            generation_result,
            validation_result
        )
        
        return ContentResponse(
            content=generation_result["final_content"],
            metadata=generation_result["content_metadata"],
            quality_score=generation_result["quality_score"],
            workflow_data=generation_result["workflow_data"],
            generation_metadata=generation_result["generation_metadata"],
            validation_result=validation_result,
            excel_export_path=generation_result.get("excel_export_path")
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Fast content generation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during fast content generation")


@app.get("/categories")
async def get_categories():
    """Get available content categories."""
    return {"categories": config.content_categories}


@app.get("/industries")
async def get_industries():
    """Get available industries."""
    return {"industries": config.industries}


@app.get("/config")
async def get_config():
    """Get public configuration information."""
    return {
        "content_categories": config.content_categories,
        "industries": config.industries,
        "content_lengths": ["short", "medium", "long"],
        "max_keywords": 10,
        "max_source_urls": 5
    }


async def log_generation_metrics(
    topic: str,
    generation_result: Dict[str, Any],
    validation_result: Dict[str, Any]
):
    """Log generation metrics for monitoring."""
    metrics = {
        "topic": topic,
        "quality_score": generation_result.get("quality_score", 0),
        "word_count": validation_result.get("metrics", {}).get("word_count", 0),
        "refinement_applied": generation_result.get("generation_metadata", {}).get("refinement_applied", False),
        "validation_issues": len(validation_result.get("issues", [])),
        "validation_warnings": len(validation_result.get("warnings", []))
    }
    
    logger.info(f"Generation metrics: {metrics}")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": int(time.time())
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=config.api.host,
        port=config.api.port,
        workers=1,  # Use 1 worker for development
        reload=True
    )
