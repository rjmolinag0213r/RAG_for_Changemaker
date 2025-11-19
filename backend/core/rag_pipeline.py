"""RAG Pipeline implementation."""

from typing import List, Dict, Any, Optional
from backend.core.vector_store import VectorStore
from backend.core.llm import LLMModel
from backend.config import settings
from backend.utils.logger import log


class RAGPipeline:
    """Complete RAG pipeline for question answering."""
    
    def __init__(self):
        """Initialize the RAG pipeline."""
        log.info("Initializing RAG Pipeline")
        
        self.vector_store = VectorStore()
        self.llm = LLMModel()
        
        log.info("RAG Pipeline initialized successfully")
    
    def _create_rag_prompt(self, query: str, context: str) -> List[Dict[str, str]]:
        """
        Create a prompt for RAG using retrieved context.
        
        Args:
            query: User question
            context: Retrieved context
            
        Returns:
            List of messages for chat format
        """
        system_message = """You are a helpful AI assistant that answers questions based on the provided context. 

Instructions:
- Answer the question using ONLY the information provided in the context below
- Be concise and accurate
- If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer that question based on the provided documents."
- Do not make up information or use knowledge outside of the provided context
- If appropriate, cite which document or source the information comes from"""
        
        user_message = f"""Context:
{context}

Question: {query}

Please provide a clear and accurate answer based on the context above."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        return messages
    
    def query(
        self, 
        question: str,
        n_results: Optional[int] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a RAG query.
        
        Args:
            question: User question
            n_results: Number of context chunks to retrieve
            filter_dict: Metadata filter for retrieval
            return_sources: Whether to return source documents
            
        Returns:
            Dictionary with answer and optional sources
        """
        try:
            log.info(f"Processing query: '{question}'")
            
            # Step 1: Retrieve relevant context
            retrieved_docs = self.vector_store.search(
                query=question,
                n_results=n_results,
                filter_dict=filter_dict
            )
            
            if not retrieved_docs:
                log.warning("No relevant documents found")
                return {
                    "answer": "I couldn't find any relevant information to answer your question. Please try uploading more documents or rephrasing your question.",
                    "sources": [],
                    "num_sources": 0
                }
            
            # Filter by relevance threshold
            filtered_docs = [
                doc for doc in retrieved_docs 
                if doc['relevance_score'] >= settings.rag.relevance_threshold
            ]
            
            if not filtered_docs:
                log.warning("No documents met the relevance threshold")
                filtered_docs = retrieved_docs[:1]  # Take at least one result
            
            # Step 2: Prepare context
            context_parts = []
            for i, doc in enumerate(filtered_docs, 1):
                source = doc['metadata'].get('source', 'Unknown')
                text = doc['text']
                context_parts.append(f"[Document {i} - Source: {source}]\n{text}")
            
            context = "\n\n".join(context_parts)
            
            log.info(f"Retrieved {len(filtered_docs)} relevant documents")
            
            # Step 3: Generate answer using LLM
            messages = self._create_rag_prompt(question, context)
            answer = self.llm.generate_chat_response(messages)
            
            # Step 4: Prepare response
            response = {
                "answer": answer,
                "num_sources": len(filtered_docs)
            }
            
            if return_sources:
                sources = []
                for doc in filtered_docs:
                    source_info = {
                        "text": doc['text'][:500] + "..." if len(doc['text']) > 500 else doc['text'],
                        "metadata": doc['metadata'],
                        "relevance_score": round(doc['relevance_score'], 3)
                    }
                    sources.append(source_info)
                
                response["sources"] = sources
            
            log.info("Query processed successfully")
            return response
            
        except Exception as e:
            log.error(f"Error processing query: {e}")
            raise
    
    def add_documents_from_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add document chunks to the vector store.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Result dictionary with document IDs
        """
        try:
            doc_ids = self.vector_store.add_documents(chunks)
            return {
                "success": True,
                "num_documents": len(doc_ids),
                "document_ids": doc_ids
            }
        except Exception as e:
            log.error(f"Error adding documents: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dictionary with system statistics
        """
        try:
            total_docs = self.vector_store.count_documents()
            
            # Get unique sources
            all_docs = self.vector_store.get_all_documents()
            sources = set()
            for doc in all_docs:
                source = doc['metadata'].get('source', 'Unknown')
                sources.add(source)
            
            stats = {
                "total_documents": total_docs,
                "unique_sources": len(sources),
                "sources": list(sources)
            }
            
            return stats
            
        except Exception as e:
            log.error(f"Error getting statistics: {e}")
            raise
