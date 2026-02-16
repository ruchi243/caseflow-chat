"""
Document API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from datetime import datetime
from redis import Redis
from rq import Queue

from app.models.base import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.config import settings

# Redis connection for job queue
redis_conn = Redis(host='localhost', port=6379, decode_responses=True)
task_queue = Queue('documents', connection=redis_conn)

router = APIRouter(prefix="/cases/{case_id}/documents", tags=["Documents"])

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    case_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing
    
    Accepts PDF and DOCX files up to 10MB.
    Processing happens in background job.
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Create uploads directory
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"case_{case_id}_{timestamp}_{file.filename}"
    file_path = upload_dir / safe_filename
    
    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create document record
    db_document = Document(
        case_id=case_id,
        filename=file.filename,
        file_path=str(file_path),
        mime_type=file.content_type or "application/octet-stream"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    # Process document immediately (synchronous)
    job_id = None
    try:
        from app.workers.document_worker import process_document
        result = process_document(db_document.id)
        message = f"✅ Document processed: {result['chunks_created']} chunks created"
    except Exception as e:
        print(f"⚠️  Processing error: {e}")
        import traceback
        traceback.print_exc()
        message = f"Document uploaded but processing failed: {str(e)}"
    
  
    
    return DocumentUploadResponse(
        document=DocumentResponse.from_orm(db_document),
        job_id=job_id,
        message=message
    )


@router.get("/", response_model=list[DocumentResponse])
def list_documents(
    case_id: int,
    db: Session = Depends(get_db)
):
    """List all documents for a case"""
    documents = db.query(Document).filter(Document.case_id == case_id).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    case_id: int,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.case_id == case_id
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc