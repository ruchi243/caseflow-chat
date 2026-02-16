"""
Background Worker for Document Processing
"""
from sqlalchemy.orm import Session
from pathlib import Path

from app.models.base import SessionLocal
from app.models.document import Document
from app.utils.document_processor import document_processor
from app.utils.chunking import chunk_text
from app.services.rag_service import rag_service


def process_document(document_id: int):
    """
    Process uploaded document
    
    1. Extract text from PDF/DOCX
    2. Chunk the text
    3. Add to vector database
    4. Update document record
    """
    db = SessionLocal()
    
    try:
        # Get document from database
        doc = db.query(Document).filter(Document.id == document_id).first()
        
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        
        print(f"🔄 Processing document: {doc.filename}")
        
        # 1. Extract text
        extracted_text = document_processor.extract_text(doc.file_path)
        
        print(f"   ✅ Extracted {len(extracted_text)} characters")
        
        # 2. Chunk text
        chunks = chunk_text(extracted_text, chunk_size=500, overlap=50)
        
        print(f"   ✅ Created {len(chunks)} chunks")
        
        # 3. Add to vector database
        rag_service.add_document_chunks(
            chunks=chunks,
            doc_id=f"doc_{document_id}",
            source_doc=doc.filename,
            metadata={
                "case_id": doc.case_id,
                "doc_type": "user_upload",
                "mime_type": doc.mime_type
            }
        )
        
        print(f"   ✅ Added to vector database")
        
        # 4. Update document record with extracted text
        doc.extracted_text = extracted_text
        db.commit()
        
        print(f"✅ Document {doc.filename} processed successfully!")
        
        return {
            "success": True,
            "document_id": document_id,
            "chunks_created": len(chunks),
            "text_length": len(extracted_text)
        }
    
    except Exception as e:
        print(f"❌ Error processing document {document_id}: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()