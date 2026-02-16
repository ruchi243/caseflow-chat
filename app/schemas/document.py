"""
Pydantic schemas for Document API
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: int
    case_id: int
    filename: str
    mime_type: str
    uploaded_at: datetime
    extracted_text: Optional[str] = None
    
    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Response after uploading document"""
    document: DocumentResponse
    job_id: Optional[str] = None
    message: str