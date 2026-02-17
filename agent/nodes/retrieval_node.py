"""Retrieval node for semantic search from MongoDB Atlas."""

from agent.state import AgentState
from utils.mongodb_handler import MongoDBHandler
import config


def retrieval_node(state: AgentState) -> AgentState:
    """Retrieve relevant documents based on query type and months."""
    
    query = state["query"]
    query_type = state.get("query_type", "intra")
    months_mentioned = state.get("months_mentioned", [])
    
    # Initialize MongoDB handler
    mongodb_handler = MongoDBHandler()
    
    try:
        # Build metadata filter
        filter_dict = None
        
        if query_type == "intra" and months_mentioned:
            # For intra-doc queries with specific month mentioned
            filter_dict = {
                "metadata.month": {"$in": months_mentioned}
            }
            k = config.TOP_K_RESULTS
        elif query_type == "intra" and not months_mentioned:
            # For intra-doc without specific month, search all
            filter_dict = None
            k = config.TOP_K_RESULTS
        else:  # inter-doc
            # For inter-doc, retrieve from all months
            if months_mentioned:
                filter_dict = {
                    "metadata.month": {"$in": months_mentioned}
                }
            else:
                filter_dict = None
            k = config.TOP_K_RESULTS * 3  # Get more results for comparison
        
        # Perform similarity search
        retrieved_docs = mongodb_handler.similarity_search(
            query=query,
            k=k,
            filter_dict=filter_dict
        )
        
        state["retrieved_docs"] = retrieved_docs
        
        if retrieved_docs:
            print(f"Retrieved {len(retrieved_docs)} documents")
            # Print sources for debugging
            sources = set([doc.metadata.get("month", "Unknown") for doc in retrieved_docs])
            print(f"Sources: {sources}")
        else:
            print("No documents retrieved")
            state["error"] = "No relevant information found in factsheets"
    
    except Exception as e:
        print(f"Error in retrieval node: {e}")
        state["error"] = f"Retrieval error: {str(e)}"
        state["retrieved_docs"] = []
    
    finally:
        mongodb_handler.close()
    
    return state