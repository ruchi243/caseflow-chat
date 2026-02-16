from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum 
from sqlalchemy import Enum

class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base):
    __tablename__ = "messages"
    
    # YOUR CODE HERE
    # Define the columns
    """
    id: Integer, primary key
case_id: Integer, foreign key to cases.id
role: String (will be "user", "assistant", or "system")
content: Text (the actual message)
created_at: Timestamp with default now()

   # message table - linked to cases via case_id. stores the conversation history for each case. is useful for tracking the dialogue and context of the case, which can be used for AI processing and generating responses.

    """
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable = False, index = True )
    role = Column(Enum(MessageRole), nullable = False)
    content = Column(Text, nullable = False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    case = relationship("Case", back_populates="messages")

    def __repr__(self):
        """String representation for debugging"""
        return f"<Message(id={self.id}, role='{self.role}', case_id={self.case_id})>"
