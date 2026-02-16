"""
this module sets up the database connection and base model for SQLAlchemy.
- `engine`: The core interface to the database, created using the connection string from settings.
- `SessionLocal`: A factory for creating new database sessions, configured to not autocommit
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
# SQLAlchemy translates Python objects → SQL queries
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Session factory - creates database sessions
# Think of session as a "transaction context"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """
Dependency function to get a database session
This is used in FastAPI endpoints to provide a session for database operations
    
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()