"""
Ollama LLM Service
Handles all interactions with Ollama
"""
from ollama import Client
from app.config import settings
from typing import List, Dict, Any


class OllamaService:
    """Service for interacting with Ollama LLM"""
    
    def __init__(self):
        self.client = Client(host=settings.ollama_host)
        self.model = "llama3.2"  # Default model
    
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = self.client.chat(
            model=self.model,
            messages=messages
        )
        
        return response['message']['content']
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (list of floats)
        """
        response = self.client.embeddings(
            model="nomic-embed-text",
            prompt=text
        )
        
        return response['embedding']
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Multi-turn conversation
        
        Args:
            messages: List of message dicts with role and content
            
        Returns:
            Generated response
        """
        response = self.client.chat(
            model=self.model,
            messages=messages
        )
        
        return response['message']['content']


# Global instance
ollama_service = OllamaService()