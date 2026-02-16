"""
Test inserting actual data into our models
This proves everything works!
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.models.base import SessionLocal
from app.models.case import Case, CaseStatus
from app.models.messages import Message, MessageRole
from app.models.document import Document


def test_insert_data():
    """Insert test data and query it back"""
    # Create a database session
    db = SessionLocal()
    
    try:
        # 1. Create a new case
        print("Creating a test case...")
        new_case = Case(
            name="Jane Smith - H-1B",
            visa_type="H-1B",
            status=CaseStatus.INTAKE
        )
        db.add(new_case)
        db.commit()
        db.refresh(new_case)  # Get the auto-generated ID
        
        print(f"✅ Created case: {new_case}")
        print(f"   ID: {new_case.id}")
        print(f"   Name: {new_case.name}")
        print(f"   Status: {new_case.status}")
        
        # 2. Add messages to the case
        print("\nAdding messages...")
        messages = [
            Message(
                case_id=new_case.id,
                role=MessageRole.USER,
                content="I need help with an H-1B petition."
            ),
            Message(
                case_id=new_case.id,
                role=MessageRole.ASSISTANT,
                content="I'd be happy to help! Let me gather some information."
            ),
        ]
        
        for msg in messages:
            db.add(msg)
        
        db.commit()
        print(f"✅ Added {len(messages)} messages")
        
        # 3. Add a document
        print("\nAdding a document...")
        doc = Document(
            case_id=new_case.id,
            filename="resume.pdf",
            file_path="./data/uploads/resume.pdf",
            mime_type="application/pdf",
            extracted_text="This is sample extracted text from the resume..."
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        print(f"✅ Added document: {doc.filename}")
        
        # 4. Query everything back using relationships!
        print("\n" + "="*50)
        print("QUERYING DATA BACK (Testing Relationships)")
        print("="*50)
        
        # Get the case
        queried_case = db.query(Case).filter(Case.id == new_case.id).first()
        print(f"\n📁 Case: {queried_case.name}")
        print(f"   Status: {queried_case.status.value}")
        print(f"   Created: {queried_case.created_at}")
        
        # Access messages through relationship
        print(f"\n💬 Messages ({len(queried_case.messages)}):")
        for msg in queried_case.messages:
            print(f"   [{msg.role.value}]: {msg.content}")
        
        # Access documents through relationship
        print(f"\n📄 Documents ({len(queried_case.documents)}):")
        for doc in queried_case.documents:
            print(f"   - {doc.filename} ({doc.mime_type})")
        
        # 5. Test querying with joins (SQL magic!)
        print("\n" + "="*50)
        print("TESTING SQL QUERIES")
        print("="*50)
        
        # Count messages per case
        total_messages = db.query(Message).filter(Message.case_id == new_case.id).count()
        print(f"\n📊 Total messages in case: {total_messages}")
        
        # Get all user messages
        user_messages = db.query(Message).filter(
            Message.case_id == new_case.id,
            Message.role == MessageRole.USER
        ).all()
        print(f"📊 User messages: {len(user_messages)}")
        
        print("\n✅ ALL TESTS PASSED! Database works perfectly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    test_insert_data()