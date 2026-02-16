"""
Seed H-1B immigration knowledge base
This creates the foundational RAG data
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.rag_service import rag_service


# H-1B Knowledge Base
H1B_KNOWLEDGE = [
    {
        "doc_id": "uscis_i129_instructions_2024",
        "source_doc": "Form I-129 Instructions for H-1B",
        "chunks": [
            {
                "text": "Required Documentation: The petitioner must submit evidence that the beneficiary has the required educational qualifications. This includes a copy of the beneficiary's degree certificate or official transcript showing completion of a bachelor's degree or higher in the specific specialty.",
                "page": 3,
                "section": "Required Documentation",
                "visa_type": "H-1B"
            },
            {
                "text": "Passport Requirements: A clear photocopy of the biographical page of the beneficiary's current passport showing the passport number, date of issue, expiration date, and photograph is required. The passport must be valid for at least six months beyond the requested period of stay.",
                "page": 3,
                "section": "Required Documentation",
                "visa_type": "H-1B"
            },
            {
                "text": "Labor Condition Application (LCA): The petitioner must submit a certified Labor Condition Application (Form ETA-9035) from the Department of Labor. The LCA must be certified before filing the I-129 petition.",
                "page": 4,
                "section": "Labor Condition Application",
                "visa_type": "H-1B"
            },
            {
                "text": "Specialty Occupation Evidence: Provide a detailed description of the job duties to establish that the position qualifies as a specialty occupation. The description should explain specific tasks, time allocation, and how duties require specialized knowledge requiring a bachelor's degree or higher.",
                "page": 5,
                "section": "Specialty Occupation Evidence",
                "visa_type": "H-1B"
            },
            {
                "text": "Employer Documentation: Submit evidence of the petitioning organization's ability to pay the offered wage. This may include annual reports, federal tax returns, audited financial statements, or quarterly wage reports.",
                "page": 6,
                "section": "Employer Evidence",
                "visa_type": "H-1B"
            }
        ]
    },
    {
        "doc_id": "h1b_checklist_2024",
        "source_doc": "H-1B Document Checklist",
        "chunks": [
            {
                "text": "PERSONAL DOCUMENTS: Passport biographical page (mandatory), Previous visa stamps if applicable, Current I-94 record if in US, Birth certificate recommended for dependent applications.",
                "page": 1,
                "section": "Personal Documents",
                "visa_type": "H-1B"
            },
            {
                "text": "EDUCATIONAL DOCUMENTS: Degree certificate or transcript (mandatory), Foreign degree evaluation if applicable, Professional licenses if required for position, Professional certifications recommended.",
                "page": 1,
                "section": "Educational Documents",
                "visa_type": "H-1B"
            },
            {
                "text": "EMPLOYMENT DOCUMENTS: Certified LCA Form ETA-9035 (mandatory), Job offer letter on company letterhead (mandatory), Detailed job description establishing specialty occupation (mandatory), Employment contract if applicable.",
                "page": 2,
                "section": "Employment Documents",
                "visa_type": "H-1B"
            }
        ]
    }
]


def seed_knowledge_base():
    """Seed the RAG database with H-1B knowledge"""
    print("🌱 Seeding H-1B Knowledge Base...\n")
    
    total_chunks = 0
    
    for doc in H1B_KNOWLEDGE:
        print(f"Processing: {doc['source_doc']}")
        
        # Extract chunks and metadata
        chunks = [chunk['text'] for chunk in doc['chunks']]
        
        # Add to RAG
        rag_service.add_document_chunks(
            chunks=chunks,
            doc_id=doc['doc_id'],
            source_doc=doc['source_doc'],
            metadata={
                "doc_type": "immigration_law",
                "visa_type": "H-1B"
            }
        )
        
        total_chunks += len(chunks)
        print(f"  ✅ Added {len(chunks)} chunks\n")
    
    # Show stats
    stats = rag_service.get_collection_stats()
    print("="*60)
    print(f"✅ Seeding Complete!")
    print(f"   Total chunks in database: {stats['total_chunks']}")
    print("="*60)


if __name__ == "__main__":
    seed_knowledge_base()