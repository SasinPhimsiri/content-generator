"""Pydantic models for API requests and responses."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class ContentRequest(BaseModel):
    """Request model for content generation."""
    
    topic: str = Field(..., min_length=3, max_length=200, description="Main topic for content generation")
    category: Optional[str] = Field(None, max_length=100, description="Content category")
    industry: Optional[str] = Field(None, max_length=100, description="Target industry")
    target_audience: Optional[str] = Field("business executives", max_length=100, description="Target audience")
    seo_keywords: Optional[List[str]] = Field([], max_items=10, description="SEO keywords to include")
    content_length: Optional[str] = Field("medium", description="Content length: short, medium, or long")
    source_urls: Optional[List[str]] = Field([], max_items=5, description="Source URLs for additional context")
    additional_context: Optional[str] = Field("", max_length=1000, description="Additional context or requirements")
    
    @validator('seo_keywords')
    def validate_keywords(cls, v):
        if v:
            return [keyword.strip() for keyword in v if keyword.strip() and len(keyword.strip()) <= 50]
        return []
    
    @validator('content_length')
    def validate_content_length(cls, v):
        if v not in ['short', 'medium', 'long']:
            return 'medium'
        return v
    
    @validator('source_urls')
    def validate_urls(cls, v):
        if v:
            valid_urls = []
            for url in v:
                if isinstance(url, str) and (url.startswith('http://') or url.startswith('https://')):
                    valid_urls.append(url)
            return valid_urls[:5]  # Limit to 5 URLs
        return []


class ContentMetadata(BaseModel):
    """Metadata for generated content."""
    
    topic: str
    category: str
    industry: str
    target_audience: str
    seo_keywords: List[str]
    estimated_word_count: int
    content_length: str
    refined: Optional[bool] = False
    refinement_reason: Optional[str] = None


class WorkflowData(BaseModel):
    """Data from the content generation workflow."""
    
    research_insights: str
    relevant_examples: List[Dict[str, Any]]
    review_suggestions: List[str]
    rewriting_improvements: Optional[Dict[str, Any]] = {}


class GenerationMetadata(BaseModel):
    """Metadata about the generation process."""
    
    workflow_completed: bool
    agents_used: List[str]
    refinement_applied: Optional[bool] = False
    rewriting_applied: Optional[bool] = False
    enhanced_mode: Optional[bool] = False
    target_quality_achieved: Optional[bool] = False


class ValidationResult(BaseModel):
    """Content validation results."""
    
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]


class ContentResponse(BaseModel):
    """Response model for content generation."""
    
    content: str = Field(..., description="Generated article content")
    metadata: ContentMetadata = Field(..., description="Content metadata")
    quality_score: float = Field(..., ge=0, le=10, description="Quality score from 0-10")
    workflow_data: WorkflowData = Field(..., description="Workflow execution data")
    generation_metadata: GenerationMetadata = Field(..., description="Generation process metadata")
    validation_result: ValidationResult = Field(..., description="Content validation results")
    excel_export_path: Optional[str] = Field(None, description="Path to exported Excel file")


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status: healthy, degraded, or unhealthy")
    timestamp: int = Field(..., description="Unix timestamp")
    version: str = Field(..., description="API version")
    model_available: bool = Field(..., description="Whether the LLM model is available")
    model_name: str = Field(..., description="Name of the LLM model")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: int = Field(..., description="Unix timestamp")
