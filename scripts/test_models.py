"""
Test our database models
"""
import sys
import os

# Add project root to Python path
# __file__ is this script's location
# Go up one level (.parent) to get to project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print(f"✅ Added to Python path: {project_root}\n")

# Now imports will work
from app.models.base import Base, engine
from app.models.case import Case, CaseStatus
from app.models.messages import Message, MessageRole
from app.models.document import Document


def test_create_tables():
    """Create all tables in the database"""
    print("Creating database tables...")
    
    # This creates all tables defined by our models
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tables created successfully!")
    print("\nTables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


if __name__ == "__main__":
    test_create_tables()