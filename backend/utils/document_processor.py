
"""Document processing utilities for PDF and text extraction."""

import io
from pathlib import Path
from typing import List, Dict, Any, Optional
import PyPDF2
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.config import settings
from backend.utils.logger import log


class DocumentProcessor:
    """Handle document processing including PDF extraction and text chunking."""
    
    def __init__(self):
        """Initialize the document processor."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.text_processing.chunk_size,
            chunk_overlap=settings.text_processing.chunk_overlap,
            separators=settings.text_processing.separators,
            length_function=len,
        )
        log.info("DocumentProcessor initialized")
    
    def extract_text_from_pdf(self, pdf_file: bytes, filename: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_file: PDF file content as bytes
            filename: Name of the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        try:
            log.info(f"Extracting text from PDF: {filename}")
            
            # Try pdfplumber first (better for complex PDFs)
            try:
                with pdfplumber.open(io.BytesIO(pdf_file)) as pdf:
                    text = ""
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
                    
                    if text.strip():
                        log.info(f"Successfully extracted {len(text)} characters using pdfplumber")
                        return text.strip()
            except Exception as e:
                log.warning(f"pdfplumber failed, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            log.info(f"Successfully extracted {len(text)} characters using PyPDF2")
            return text.strip()
            
        except Exception as e:
            log.error(f"Error extracting text from PDF {filename}: {e}")
            raise
    
    def chunk_text(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.
        
        Args:
            text: Text to chunk
            metadata: Additional metadata to attach to each chunk
            
        Returns:
            List of chunks with metadata
        """
        try:
            log.info(f"Chunking text of length {len(text)}")
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create chunk objects with metadata
            chunk_objects = []
            for i, chunk in enumerate(chunks):
                chunk_obj = {
                    "text": chunk,
                    "chunk_index": i,
                    "metadata": metadata or {}
                }
                chunk_objects.append(chunk_obj)
            
            log.info(f"Created {len(chunk_objects)} chunks")
            return chunk_objects
            
        except Exception as e:
            log.error(f"Error chunking text: {e}")
            raise
    
    def process_pdf(
        self, 
        pdf_file: bytes, 
        filename: str, 
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a PDF file: extract text and create chunks.
        
        Args:
            pdf_file: PDF file content as bytes
            filename: Name of the PDF file
            additional_metadata: Additional metadata to attach
            
        Returns:
            List of text chunks with metadata
        """
        try:
            # Extract text
            text = self.extract_text_from_pdf(pdf_file, filename)
            
            # Prepare metadata
            metadata = {
                "source": filename,
                "source_type": "pdf",
                **(additional_metadata or {})
            }
            
            # Chunk text
            chunks = self.chunk_text(text, metadata)
            
            log.info(f"Successfully processed PDF {filename} into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            log.error(f"Error processing PDF {filename}: {e}")
            raise
    
    def process_text(
        self, 
        text: str, 
        source_name: str,
        source_type: str = "text",
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process raw text: create chunks with metadata.
        
        Args:
            text: Raw text to process
            source_name: Name/identifier of the source
            source_type: Type of source (e.g., "web", "text")
            additional_metadata: Additional metadata to attach
            
        Returns:
            List of text chunks with metadata
        """
        try:
            # Prepare metadata
            metadata = {
                "source": source_name,
                "source_type": source_type,
                **(additional_metadata or {})
            }
            
            # Chunk text
            chunks = self.chunk_text(text, metadata)
            
            log.info(f"Successfully processed text from {source_name} into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            log.error(f"Error processing text from {source_name}: {e}")
            raise
