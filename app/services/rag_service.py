"""
RAG Service - Vector Database with Citations
Handles document storage, retrieval, and citation management
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path

from app.config import settings
from app.services.llm_service import ollama_service


class Citation:
    """Citation data structure"""
    def __init__(
        self,
        source_doc: str,
        doc_id: str,
        page: int,
        section: str,
        chunk_index: int,
        confidence: float,
        text: str = ""
    ):
        self.source_doc = source_doc
        self.doc_id = doc_id
        self.page = page
        self.section = section
        self.chunk_index = chunk_index
        self.confidence = confidence
        self.text = text
    
    def to_dict(self) -> Dict:
        return {
            "source_doc": self.source_doc,
            "doc_id": self.doc_id,
            "page": self.page,
            "section": self.section,
            "chunk_index": self.chunk_index,
            "confidence": self.confidence,
            "text": self.text[:200] + "..." if len(self.text) > 200 else self.text
        }
    
    def format(self) -> str:
        """Format citation for display"""
        return f"Source: {self.source_doc}, Section {self.section}, Page {self.page}"


class RAGService:
    """Vector database service for RAG"""
    
    def __init__(self):
        # Ensure chroma directory exists
        chroma_path = Path(settings.chroma_persist_dir)
        chroma_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client (embedded mode)
        self.client = chromadb.PersistentClient(
            path=str(chroma_path)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="immigration_knowledge",
            metadata={"description": "Immigration law and case documents"}
        )
    
    def add_document_chunks(
        self,
        chunks: List[str],
        doc_id: str,
        source_doc: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add document chunks to vector database
        
        Args:
            chunks: List of text chunks
            doc_id: Unique document identifier
            source_doc: Source document name
            metadata: Additional metadata (visa_type, section, etc.)
        """
        if not chunks:
            return
        
        # Generate embeddings for all chunks
        embeddings = []
        for chunk in chunks:
            embedding = ollama_service.generate_embedding(chunk)
            embeddings.append(embedding)
        
        # Prepare IDs and metadata
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "source_doc": source_doc,
                "doc_id": doc_id,
                "chunk_index": i,
                "page": metadata.get("page", 0) if metadata else 0,
                "section": metadata.get("section", "main") if metadata else "main",
                "doc_type": metadata.get("doc_type", "user_upload") if metadata else "user_upload"
            }
            
            # Add custom metadata if provided
            if metadata:
                for key, value in metadata.items():
                    if key not in chunk_metadata:
                        # Convert lists to strings for ChromaDB
                        if isinstance(value, list):
                            chunk_metadata[key] = str(value)
                        else:
                            chunk_metadata[key] = value
            
            metadatas.append(chunk_metadata)
        
        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        print(f"✅ Added {len(chunks)} chunks from {source_doc} to vector DB")
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search vector database
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filter (e.g., {"visa_type": "H-1B"})
            
        Returns:
            List of results with text and citations
        """
        # Generate query embedding
        query_embedding = ollama_service.generate_embedding(query)
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )
        
        # Format results with citations
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                text = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                # Convert distance to confidence (closer = higher confidence)
                confidence = max(0, 1 - (distance / 2))
                
                citation = Citation(
                    source_doc=metadata.get('source_doc', 'Unknown'),
                    doc_id=metadata.get('doc_id', 'unknown'),
                    page=metadata.get('page', 0),
                    section=metadata.get('section', 'main'),
                    chunk_index=metadata.get('chunk_index', i),
                    confidence=round(confidence, 2),
                    text=text
                )
                
                formatted_results.append({
                    "text": text,
                    "citation": citation.to_dict(),
                    "citation_formatted": citation.format()
                })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name
        }
    
    def delete_document(self, doc_id: str) -> None:
        """Delete all chunks for a document"""
        # Get all IDs for this document
        results = self.collection.get(
            where={"doc_id": doc_id}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            print(f"✅ Deleted {len(results['ids'])} chunks for document {doc_id}")


# Global instance
rag_service = RAGService()