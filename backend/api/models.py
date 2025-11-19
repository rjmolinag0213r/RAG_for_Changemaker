
"""API data models."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class UploadPDFResponse(BaseModel):
    """Response for PDF upload."""
    success: bool
    message: str
    num_chunks: int
    document_ids: List[str]


class ScrapeURLRequest(BaseModel):
    """Request for URL scraping."""
    url: HttpUrl
    include_links: Optional[bool] = False


class ScrapeURLResponse(BaseModel):
    """Response for URL scraping."""
    success: bool
    message: str
    num_chunks: int
    document_ids: List[str]
    title: Optional[str] = None


class QueryRequest(BaseModel):
    """Request for RAG query."""
    question: str = Field(..., min_length=1, max_length=1000)
    n_results: Optional[int] = Field(None, ge=1, le=20)
    return_sources: Optional[bool] = True


class Source(BaseModel):
    """Source document information."""
    text: str
    metadata: Dict[str, Any]
    relevance_score: float


class QueryResponse(BaseModel):
    """Response for RAG query."""
    answer: str
    num_sources: int
    sources: Optional[List[Source]] = None


class Document(BaseModel):
    """Document information."""
    id: str
    text: str
    metadata: Dict[str, Any]


class DocumentsResponse(BaseModel):
    """Response for listing documents."""
    total_documents: int
    documents: List[Document]


class DeleteResponse(BaseModel):
    """Response for delete operations."""
    success: bool
    message: str


class StatsResponse(BaseModel):
    """Response for system statistics."""
    total_documents: int
    unique_sources: int
    sources: List[str]


class HealthResponse(BaseModel):
    """Response for health check."""
    status: str
    version: str
    vector_store_status: str
    llm_status: str
