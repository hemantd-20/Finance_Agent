"""MongoDB Atlas vector store handler."""

from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document
from typing import List, Optional
import config
from utils.embeddings import EmbeddingHandler


class MongoDBHandler:
    """Handle MongoDB Atlas vector store operations."""
    
    def __init__(self):
        self.client = MongoClient(config.MONGODB_URI)
        self.db = self.client[config.MONGODB_DB_NAME]
        self.collection = self.db[config.MONGODB_COLLECTION_NAME]
        self.embedding_handler = EmbeddingHandler()
        
        # Initialize vector store
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.collection,
            embedding=self.embedding_handler.get_embeddings_model(),
            index_name="vector_index_1",
            text_key="text",
            embedding_key="embedding"
        )
    
    def create_vector_index(self):
        """Create vector search index in MongoDB Atlas."""
        # Note: This index must be created manually in MongoDB Atlas UI
        # or using Atlas CLI with the following configuration:
        # IMPORTANT: LangChain MongoDB stores metadata as top-level fields, not nested
        index_config = {
            "name": "vector_index_1",
            "type": "vectorSearch",
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 1024,  # BGE-M3 embedding dimension
                        "similarity": "cosine"
                    },
                    {
                        "type": "filter",
                        "path": "month"  # Top-level field, not metadata.month
                    },
                    {
                        "type": "filter",
                        "path": "fund_name"  # Top-level field, not metadata.fund_name
                    }
                ]
            }
        }
        print("Please create the vector index manually in MongoDB Atlas with this config:")
        print(index_config)
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store."""
        try:
            self.vector_store.add_documents(documents)
            print(f"Successfully added {len(documents)} documents to MongoDB Atlas")
        except Exception as e:
            print(f"Error adding documents to MongoDB: {e}")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = config.TOP_K_RESULTS,
        filter_dict: Optional[dict] = None
    ) -> List[Document]:
        """Perform similarity search with optional metadata filtering."""
        try:
            print(f"DEBUG MongoDB - Query: {query[:100]}...")
            print(f"DEBUG MongoDB - k: {k}")
            print(f"DEBUG MongoDB - filter_dict: {filter_dict}")
            
            if filter_dict:
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k,
                    pre_filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k
                )
            
            print(f"DEBUG MongoDB - Results count: {len(results)}")
            if results:
                print(f"DEBUG MongoDB - First result metadata: {results[0].metadata}")
            
            return results
        except Exception as e:
            print(f"Error performing similarity search: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = config.TOP_K_RESULTS,
        filter_dict: Optional[dict] = None
    ) -> List[tuple]:
        """Perform similarity search and return results with scores."""
        try:
            if filter_dict:
                results = self.vector_store.similarity_search_with_score(
                    query=query,
                    k=k,
                    pre_filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search_with_score(
                    query=query,
                    k=k
                )
            return results
        except Exception as e:
            print(f"Error performing similarity search with score: {e}")
            return []
    
    def delete_all_documents(self):
        """Delete all documents from the collection."""
        try:
            self.collection.delete_many({})
            print("All documents deleted from MongoDB Atlas")
        except Exception as e:
            print(f"Error deleting documents: {e}")
    
    def close(self):
        """Close MongoDB connection."""
        self.client.close()