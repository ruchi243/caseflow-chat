"""
Agent API endpoint - chat with the AI
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.base import get_db
from app.models.case import Case
from app.models.messages import Message, MessageRole
from app.services.agent_service import run_agent

router = APIRouter(prefix="/cases/{case_id}/chat", tags=["Agent"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    tools_used: list
    profile: dict
    citations: list


@router.post("/", response_model=ChatResponse)
def chat_with_agent(
    case_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with the AI agent
    
    The agent will:
    - Extract profile information
    - Answer questions using RAG
    - Generate checklists
    - Draft letters
    """
    # Get case
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get conversation history
    messages = db.query(Message).filter(Message.case_id == case_id).all()
    history = [{"role": m.role.value, "content": m.content} for m in messages]
    
    # Get profile (simplified - you'd load from case_profiles table)
    profile = {}
    
    # Run agent
    result = run_agent(
        message=request.message,
        conversation_history=history,
        profile=profile,
        case_id=case_id
    )
    
    # Save messages
    db.add(Message(case_id=case_id, role=MessageRole.USER, content=request.message))
    db.add(Message(case_id=case_id, role=MessageRole.ASSISTANT, content=result['response']))
    db.commit()
    
    return ChatResponse(
        response=result['response'],
        tools_used=result['tools_used'],
        profile=result['updated_profile'],
        citations=result['citations']
    )