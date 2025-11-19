
"""API routes for the RAG system."""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from backend.api.models import (
    UploadPDFResponse, ScrapeURLRequest, ScrapeURLResponse,
    QueryRequest, QueryResponse, DocumentsResponse, DeleteResponse,
    StatsResponse, HealthResponse
)
from backend.core.rag_pipeline import RAGPipeline
from backend.utils.document_processor import DocumentProcessor
from backend.utils.web_scraper import WebScraper
from backend.utils.logger import log
from backend.config import settings

# Initialize components
rag_pipeline = RAGPipeline()
doc_processor = DocumentProcessor()
web_scraper = WebScraper()

# Create router
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health."""
    try:
        # Check vector store
        vector_store_status = "healthy"
        try:
            rag_pipeline.vector_store.count_documents()
        except Exception as e:
            vector_store_status = f"unhealthy: {str(e)}"
        
        # Check LLM
        llm_status = "healthy"
        if rag_pipeline.llm.model is None:
            llm_status = "unhealthy: model not loaded"
        
        return HealthResponse(
            status="healthy" if vector_store_status == "healthy" and llm_status == "healthy" else "degraded",
            version=settings.app.version,
            vector_store_status=vector_store_status,
            llm_status=llm_status
        )
    except Exception as e:
        log.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-pdf", response_model=UploadPDFResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file.
    
    Args:
        file: PDF file to upload
        
    Returns:
        Upload result with document IDs
    """
    try:
        log.info(f"Received PDF upload: {file.filename}")
        
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a PDF"
            )
        
        # Read file content
        content = await file.read()
        
        # Process PDF
        chunks = doc_processor.process_pdf(content, file.filename)
        
        # Add to vector store
        result = rag_pipeline.add_documents_from_chunks(chunks)
        
        log.info(f"Successfully processed PDF: {file.filename}")
        
        return UploadPDFResponse(
            success=True,
            message=f"Successfully processed {file.filename}",
            num_chunks=result['num_documents'],
            document_ids=result['document_ids']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error processing PDF upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.post("/scrape-url", response_model=ScrapeURLResponse)
async def scrape_url(request: ScrapeURLRequest):
    """
    Scrape and process content from a URL.
    
    Args:
        request: URL scraping request
        
    Returns:
        Scraping result with document IDs
    """
    try:
        url = str(request.url)
        log.info(f"Received URL scraping request: {url}")
        
        # Scrape URL
        scraped_data = web_scraper.scrape_url(url)
        
        # Check if content was extracted
        if not scraped_data['text']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content could be extracted from the URL"
            )
        
        # Process the scraped text
        chunks = doc_processor.process_text(
            text=scraped_data['text'],
            source_name=url,
            source_type='web',
            additional_metadata={
                'title': scraped_data.get('title', ''),
                'url': url
            }
        )
        
        # Add to vector store
        result = rag_pipeline.add_documents_from_chunks(chunks)
        
        log.info(f"Successfully processed URL: {url}")
        
        return ScrapeURLResponse(
            success=True,
            message=f"Successfully scraped and indexed content from {url}",
            num_chunks=result['num_documents'],
            document_ids=result['document_ids'],
            title=scraped_data.get('title')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error processing URL scraping: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scraping URL: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Execute a RAG query.
    
    Args:
        request: Query request with question
        
    Returns:
        Answer with sources
    """
    try:
        log.info(f"Received query: {request.question}")
        
        # Execute RAG query
        result = rag_pipeline.query(
            question=request.question,
            n_results=request.n_results,
            return_sources=request.return_sources
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        log.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/documents", response_model=DocumentsResponse)
async def get_documents():
    """
    Get all indexed documents.
    
    Returns:
        List of all documents with metadata
    """
    try:
        documents = rag_pipeline.vector_store.get_all_documents()
        
        return DocumentsResponse(
            total_documents=len(documents),
            documents=documents
        )
        
    except Exception as e:
        log.error(f"Error getting documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}"
        )


@router.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str):
    """
    Delete a document by ID.
    
    Args:
        document_id: ID of document to delete
        
    Returns:
        Deletion result
    """
    try:
        rag_pipeline.vector_store.delete_document(document_id)
        
        return DeleteResponse(
            success=True,
            message=f"Document {document_id} deleted successfully"
        )
        
    except Exception as e:
        log.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )


@router.delete("/documents/source/{source_name}", response_model=DeleteResponse)
async def delete_documents_by_source(source_name: str):
    """
    Delete all documents from a specific source.
    
    Args:
        source_name: Source identifier
        
    Returns:
        Deletion result
    """
    try:
        count = rag_pipeline.vector_store.delete_documents_by_source(source_name)
        
        return DeleteResponse(
            success=True,
            message=f"Deleted {count} documents from source: {source_name}"
        )
        
    except Exception as e:
        log.error(f"Error deleting documents by source: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting documents: {str(e)}"
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get system statistics.
    
    Returns:
        System statistics
    """
    try:
        stats = rag_pipeline.get_statistics()
        return StatsResponse(**stats)
        
    except Exception as e:
        log.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@router.delete("/clear", response_model=DeleteResponse)
async def clear_all_documents():
    """
    Clear all documents from the vector store.
    
    Returns:
        Deletion result
    """
    try:
        rag_pipeline.vector_store.clear_collection()
        
        return DeleteResponse(
            success=True,
            message="All documents cleared successfully"
        )
        
    except Exception as e:
        log.error(f"Error clearing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing documents: {str(e)}"
        )
