"""Embeddings generation utilities."""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
import config


class EmbeddingHandler:
    """Handle embeddings generation using Google's embedding model."""
    
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            google_api_key=config.GOOGLE_API_KEY
        )
    
    def generate_embedding(self, text: str) -> list:
        """Generate embedding for a single text."""
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def generate_embeddings(self, texts: list) -> list:
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