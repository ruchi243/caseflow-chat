"""
Pydantic schemas for Case API
These define the JSON structure for requests/responses
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.case import CaseStatus


class CaseBase(BaseModel):
    """Base schema - shared fields"""
    name: str = Field(..., min_length=1, max_length=200, description="Case name")
    visa_type: Optional[str] = Field(None, max_length=50, description="Visa type (e.g., H-1B)")


class CaseCreate(CaseBase):
    """Schema for creating a case (POST request)"""
    # Inherits name and visa_type from CaseBase
    # No ID needed - database generates it
    pass


class CaseUpdate(BaseModel):
    """Schema for updating a case (PATCH request)"""
    # All fields optional for partial updates
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    visa_type: Optional[str] = Field(None, max_length=50)
    status: Optional[CaseStatus] = None


class CaseResponse(CaseBase):
    """Schema for case response (what API returns)"""
    id: int
    status: CaseStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        # Allows Pydantic to work with SQLAlchemy models
        from_attributes = True


class CaseListResponse(BaseModel):
    """Schema for listing multiple cases"""
    cases: list[CaseResponse]
    total: int