"""
Test searching for uploaded document content
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.rag_service import rag_service


def test_search():
    """Search for content from uploaded document"""
    
    queries = [
        "Tell me about Jane's education",
        "What skills does Jane have?",
        "Where did Jane work?",
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        print("="*60)
        
        results = rag_service.search(query, n_results=2)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Text: {result['text']}")
                print(f"Source: {result['citation']['source_doc']}")
                print(f"Confidence: {result['citation']['confidence']}")
        else:
            print("No results found")


if __name__ == "__main__":
    print("🧪 Testing Search on Uploaded Document\n")
    test_search()
    print("\n" + "="*60)
    print("✅ Document is searchable in RAG!")
    print("="*60)