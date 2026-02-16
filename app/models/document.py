from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Document(Base):
    """
    Document table - stores uploaded files for each case.
    
    Each case can have multiple documents (resume, passport, etc.)
    We extract text from PDFs/DOCX and store it for RAG processing.
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Which case does this document belong to?
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, index=True)
    
    # Original filename (e.g., "john_resume.pdf")
    filename = Column(String, nullable=False)
    
    # Where we stored it on disk (e.g., "./data/uploads/case_1_resume.pdf")
    file_path = Column(String, nullable=False)
    
    # File type (e.g., "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    mime_type = Column(String, nullable=False)
    
    # Extracted text content (nullable - we extract this after upload)
    extracted_text = Column(Text, nullable=True)
    
    # When was this uploaded?
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship - lets you do: document.case.name
    case = relationship("Case", back_populates="documents")
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Document(id={self.id}, filename='{self.filename}', case_id={self.case_id})>"