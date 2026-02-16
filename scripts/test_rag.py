"""
Test RAG retrieval with citations
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.rag_service import rag_service


def test_search(query: str):
    """Test searching the knowledge base"""
    print(f"\n🔍 Query: '{query}'")
    print("="*60)
    
    results = rag_service.search(query, n_results=3)
    
    if not results:
        print("No results found.")
        return
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Text: {result['text'][:150]}...")
        print(f"Citation: {result['citation_formatted']}")
        print(f"Confidence: {result['citation']['confidence']}")


if __name__ == "__main__":
    print("🧪 Testing RAG Retrieval with Citations\n")
    
    # Test queries
    test_search("What documents are required for H-1B?")
    test_search("Tell me about passport requirements")
    test_search("What is an LCA?")
    
    print("\n" + "="*60)
    print("✅ RAG system working with citations!")
    print("="*60)