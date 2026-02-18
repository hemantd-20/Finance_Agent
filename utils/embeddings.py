"""Embeddings generation utilities."""

from langchain_huggingface import HuggingFaceEmbeddings
import config
from typing import List


# Global cache for the embedding model (singleton pattern)
_embedding_model_cache = None


class EmbeddingHandler:
    """Handle embeddings generation using BGE-M3 model."""
    
    def __init__(self):
        """Initialize BGE-M3 embedding model.
        
        BGE-M3 is a multilingual embedding model that:
        - Supports 100+ languages
        - Generates 1024-dimensional embeddings
        - Handles up to 8192 tokens
        - Runs locally (no API rate limits)
        """
        global _embedding_model_cache
        
        # Use cached model if available
        if _embedding_model_cache is not None:
            self.embeddings = _embedding_model_cache
            print("Using cached BGE-M3 embedding model")
        else:
            model_kwargs = {'device': 'cpu'}  # Use 'cuda' if GPU is available
            encode_kwargs = {
                'normalize_embeddings': True,  # Normalize embeddings for cosine similarity
                'batch_size': 32
            }
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name=config.EMBEDDING_MODEL,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            
            # Cache the model for future use
            _embedding_model_cache = self.embeddings
            
            print(f"Initialized BGE-M3 embedding model: {config.EMBEDDING_MODEL}")
            print("Model will run locally - no API rate limits!")
    
    def generate_embedding(self, text: str) -> list:
        """Generate embedding for a single text."""
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def generate_embeddings(self, texts: List[str]) -> list:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []
    
    def get_embeddings_model(self):
        """Return the embeddings model instance."""
        return self.embeddings
