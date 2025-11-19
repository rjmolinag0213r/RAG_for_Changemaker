
"""Vector store implementation using ChromaDB."""

import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from backend.config import settings
from backend.utils.logger import log


class VectorStore:
    """Handle vector storage and retrieval using ChromaDB."""
    
    def __init__(self):
        """Initialize ChromaDB and embedding model."""
        log.info("Initializing VectorStore")
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.chromadb.persist_directory,
                anonymized_telemetry=False
            )
        )
        
        # Initialize embedding model
        log.info(f"Loading embedding model: {settings.chromadb.embedding_model}")
        self.embedding_model = SentenceTransformer(settings.chromadb.embedding_model)
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        log.info("VectorStore initialized successfully")
    
    def _get_or_create_collection(self):
        """Get or create the ChromaDB collection."""
        try:
            collection = self.client.get_or_create_collection(
                name=settings.chromadb.collection_name,
                metadata={"hnsw:space": settings.chromadb.distance_metric}
            )
            log.info(f"Collection '{settings.chromadb.collection_name}' ready")
            return collection
        except Exception as e:
            log.error(f"Error creating/getting collection: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            log.error(f"Error generating embedding: {e}")
            raise
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Add document chunks to the vector store.
        
        Args:
            chunks: List of document chunks with text and metadata
            
        Returns:
            List of document IDs
        """
        try:
            log.info(f"Adding {len(chunks)} documents to vector store")
            
            # Prepare data for ChromaDB
            ids = []
            texts = []
            embeddings = []
            metadatas = []
            
            for chunk in chunks:
                # Generate unique ID
                doc_id = str(uuid.uuid4())
                ids.append(doc_id)
                
                # Extract text
                text = chunk['text']
                texts.append(text)
                
                # Generate embedding
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)
                
                # Prepare metadata
                metadata = chunk.get('metadata', {})
                metadata['chunk_index'] = chunk.get('chunk_index', 0)
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            log.info(f"Successfully added {len(ids)} documents")
            return ids
            
        except Exception as e:
            log.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self, 
        query: str, 
        n_results: int = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_dict: Metadata filter
            
        Returns:
            List of search results with text and metadata
        """
        try:
            if n_results is None:
                n_results = settings.rag.retrieval_k
            
            log.info(f"Searching for: '{query}' (top {n_results} results)")
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_dict,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    result = {
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'relevance_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                    }
                    formatted_results.append(result)
            
            log.info(f"Found {len(formatted_results)} relevant documents")
            return formatted_results
            
        except Exception as e:
            log.error(f"Error searching documents: {e}")
            raise
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents from the collection.
        
        Returns:
            List of all documents with metadata
        """
        try:
            results = self.collection.get(
                include=['documents', 'metadatas']
            )
            
            documents = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    doc = {
                        'id': results['ids'][i],
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    }
                    documents.append(doc)
            
            log.info(f"Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            log.error(f"Error getting all documents: {e}")
            raise
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[doc_id])
            log.info(f"Deleted document: {doc_id}")
            return True
        except Exception as e:
            log.error(f"Error deleting document {doc_id}: {e}")
            raise
    
    def delete_documents_by_source(self, source: str) -> int:
        """
        Delete all documents from a specific source.
        
        Args:
            source: Source identifier
            
        Returns:
            Number of documents deleted
        """
        try:
            # Get documents with the specified source
            results = self.collection.get(
                where={"source": source},
                include=['metadatas']
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                count = len(results['ids'])
                log.info(f"Deleted {count} documents from source: {source}")
                return count
            
            return 0
            
        except Exception as e:
            log.error(f"Error deleting documents from source {source}: {e}")
            raise
    
    def count_documents(self) -> int:
        """
        Get total number of documents in the collection.
        
        Returns:
            Document count
        """
        try:
            count = self.collection.count()
            return count
        except Exception as e:
            log.error(f"Error counting documents: {e}")
            raise
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.
        
        Returns:
            True if successful
        """
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(settings.chromadb.collection_name)
            self.collection = self._get_or_create_collection()
            log.info("Collection cleared successfully")
            return True
        except Exception as e:
            log.error(f"Error clearing collection: {e}")
            raise
