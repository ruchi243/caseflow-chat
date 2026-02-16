"""
Case Model
==========
Represents an immigration case.

This is SQLAlchemy ORM - maps Python class to SQL table.
You write Python, SQLAlchemy writes SQL!
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.messages import Message
from app.models.document import Document
from app.models.base import Base 

import enum

from app.models.base import Base


class CaseStatus(str, enum.Enum):
    """
    Enum for case status.
    Why enum? Type safety + prevents typos + autocomplete in IDE
    What is enum? A set of named values - like a dropdown in code. 
    """
    INTAKE = "intake"
    PENDING_DOCUMENTS = "pending_documents"
    READY_FOR_REVIEW = "ready_for_review"


class Case(Base):
    """
    Case table - the main entity.
    
    SQLAlchemy will create this SQL:
    
    CREATE TABLE cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR NOT NULL,
        visa_type VARCHAR,
        status VARCHAR DEFAULT 'intake',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    __tablename__ = "cases"
    
    # Primary key - auto-incrementing integer
    id = Column(Integer, primary_key=True, index=True)
    
    # Case name (e.g., "Jane Smith - H-1B")
    name = Column(String, nullable=False, index=True)
    
    # Visa type (extracted by AI later)
    visa_type = Column(String, nullable=True)
    
    # Status enum
    status = Column(
        Enum(CaseStatus),
        default=CaseStatus.INTAKE,
        nullable=False
    )
    
    # Timestamps - automatically managed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - SQLAlchemy magic!
    # This creates the join automatically
    messages = relationship("Message", back_populates="case", cascade="all, delete-orphan", lazy="select")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan", lazy="select")
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<Case(id={self.id}, name='{self.name}', status='{self.status}')>"