"""
Text Chunking Utilities
Break documents into overlapping chunks for RAG
"""
from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """
    Split text into overlapping chunks by words
    
    Args:
        text: Text to chunk
        chunk_size: Number of words per chunk
        overlap: Number of overlapping words between chunks
        
    Returns:
        List of text chunks
    
    Example:
        >>> text = "This is a sample text with many words..."
        >>> chunks = chunk_text(text, chunk_size=5, overlap=2)
        >>> # Chunk 1: "This is a sample text"
        >>> # Chunk 2: "sample text with many words"  (overlaps "sample text")
    """
    # Split into words
    words = text.split()
    
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    i = 0
    
    while i < len(words):
        # Get chunk of words
        chunk_words = words[i:i + chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
        
        # Move forward by (chunk_size - overlap)
        i += chunk_size - overlap
        
        # Prevent infinite loop if overlap >= chunk_size
        if overlap >= chunk_size:
            break
    
    return chunks


def chunk_by_sentences(
    text: str,
    max_chunk_size: int = 500
) -> List[str]:
    """
    Split text by sentences, grouping into chunks
    Better for maintaining context
    
    Args:
        text: Text to chunk
        max_chunk_size: Maximum words per chunk
        
    Returns:
        List of text chunks
    """
    import re
    
    # Split into sentences (simple approach)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        if current_size + sentence_words > max_chunk_size and current_chunk:
            # Save current chunk and start new one
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_size = sentence_words
        else:
            current_chunk.append(sentence)
            current_size += sentence_words
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks