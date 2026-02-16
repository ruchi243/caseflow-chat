"""
CRUD operations for Case model
This is the database layer - pure SQL logic
"""
from sqlalchemy.orm import Session
from app.models.case import Case, CaseStatus
from app.schemas.case import CaseCreate, CaseUpdate
from typing import Optional


def get_case(db: Session, case_id: int) -> Optional[Case]:
    """Get a single case by ID"""
    return db.query(Case).filter(Case.id == case_id).first()


def get_cases(db: Session, skip: int = 0, limit: int = 100) -> list[Case]:
    """Get all cases with pagination"""
    return db.query(Case).offset(skip).limit(limit).all()


def create_case(db: Session, case: CaseCreate) -> Case:
    """Create a new case"""
    db_case = Case(
        name=case.name,
        visa_type=case.visa_type,
        status=CaseStatus.INTAKE
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


def update_case(db: Session, case_id: int, case_update: CaseUpdate) -> Optional[Case]:
    """Update an existing case"""
    db_case = get_case(db, case_id)
    
    if not db_case:
        return None
    
    # Update only provided fields
    update_data = case_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_case, field, value)
    
    db.commit()
    db.refresh(db_case)
    return db_case


def delete_case(db: Session, case_id: int) -> bool:
    """Delete a case"""
    db_case = get_case(db, case_id)
    
    if not db_case:
        return False
    
    db.delete(db_case)
    db.commit()
    return True