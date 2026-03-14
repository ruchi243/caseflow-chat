"""
Debug: See what's actually in ChromaDB
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.rag_service import rag_service


def debug_collection():
    """Show all documents in the collection"""
    
    # Get stats
    stats = rag_service.get_collection_stats()
    print(f"📊 Total chunks in database: {stats['total_chunks']}\n")
    
    # Get all documents
    results = rag_service.collection.get()
    
    print(f"📄 Documents in collection:")
    print("="*60)
    
    if results['ids']:
        for i, doc_id in enumerate(results['ids']):
            metadata = results['metadatas'][i]
            document = results['documents'][i]
            
            print(f"\nID: {doc_id}")
            print(f"Source: {metadata.get('source_doc', 'Unknown')}")
            print(f"Doc Type: {metadata.get('doc_type', 'Unknown')}")
            print(f"Case ID: {metadata.get('case_id', 'N/A')}")
            print(f"Text Preview: {document[:100]}...")
            print("-"*60)
    else:
        print("❌ No documents found in ChromaDB!")


if __name__ == "__main__":
    print("🔍 ChromaDB Contents Debug\n")
    debug_collection()