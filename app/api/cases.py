"""
Case API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.base import get_db
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse, CaseListResponse
from app.crud import case as case_crud

# Create router
router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("/", response_model=CaseResponse, status_code=201)
def create_case(
    case: CaseCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new case
    
    Example request:
```json
    {
        "name": "John Doe - H-1B",
        "visa_type": "H-1B"
    }
```
    """
    return case_crud.create_case(db=db, case=case)


@router.get("/", response_model=CaseListResponse)
def list_cases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all cases with pagination"""
    cases = case_crud.get_cases(db=db, skip=skip, limit=limit)
    return CaseListResponse(cases=cases, total=len(cases))


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific case by ID"""
    db_case = case_crud.get_case(db=db, case_id=case_id)
    
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return db_case


@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: int,
    case_update: CaseUpdate,
    db: Session = Depends(get_db)
):
    """Update a case"""
    db_case = case_crud.update_case(db=db, case_id=case_id, case_update=case_update)
    
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return db_case


@router.delete("/{case_id}", status_code=204)
def delete_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    """Delete a case"""
    success = case_crud.delete_case(db=db, case_id=case_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return None