"""Retrieval node for semantic search from MongoDB Atlas."""

from agent.state import AgentState
from utils.mongodb_handler import MongoDBHandler
import config
import logging

logger = logging.getLogger(__name__)


def retrieval_node(state: AgentState) -> AgentState:
    """Retrieve relevant documents based on query type and months."""
    
    query = state["query"]
    query_type = state.get("query_type", "intra")
    months_mentioned = state.get("months_mentioned", [])
    
    # print(f"DEBUG - Query: {query}")
    # print(f"DEBUG - Query Type: {query_type}")
    # print(f"DEBUG - Months: {months_mentioned}")
    
    # Initialize MongoDB handler
    mongodb_handler = MongoDBHandler()
    
    try:
        # Build metadata filter
        filter_dict = None
        
        if query_type == "intra" and months_mentioned:
            # For intra-doc queries with specific month mentioned
            filter_dict = {
                "month": {"$in": months_mentioned}
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
                    "month": {"$in": months_mentioned}
                }
            else:
                filter_dict = None
            k = config.TOP_K_RESULTS * 3  # Get more results for comparison
        
        print(f"DEBUG - Filter: {filter_dict}")
        print(f"DEBUG - k: {k}")
        
        # Perform similarity search with scores (Requirements 3.1, 3.2, 3.3, 3.4, 3.5)
        results_with_scores = mongodb_handler.similarity_search_with_score(
            query=query,
            k=k,
            filter_dict=filter_dict
        )
        
        # Extract documents and scores
        retrieved_docs = [doc for doc, score in results_with_scores]
        similarity_scores = [float(score) for doc, score in results_with_scores]
        
        state["retrieved_docs"] = retrieved_docs
        
        # Extract metadata for Langfuse span (Requirements 3.1, 3.2, 3.3, 3.4, 3.5)
        document_ids = []
        months_retrieved = set()
        sources_retrieved = set()
        
        for doc in retrieved_docs:
            # Extract document ID (use page_number + month as unique identifier)
            doc_id = f"{doc.metadata.get('month', 'unknown')}_{doc.metadata.get('page_number', 'unknown')}"
            document_ids.append(doc_id)
            
            # Extract month and source
            month = doc.metadata.get("month")
            if month:
                months_retrieved.add(month)
            
            source = doc.metadata.get("source")
            if source:
                sources_retrieved.add(source)
        
        # Add custom metadata to retrieval span (Requirements 3.1, 3.2, 3.3, 3.4, 3.5)
        try:
            from langfuse.decorators import langfuse_context
            
            # Update current observation (span) with retrieval metadata
            langfuse_context.update_current_observation(
                metadata={
                    "query_text": query,
                    "k_value": k,
                    "metadata_filter": filter_dict,
                    "num_retrieved": len(retrieved_docs),
                    "document_ids": document_ids,
                    "similarity_scores": similarity_scores,
                    "months_retrieved": sorted(list(months_retrieved)),
                    "sources_retrieved": sorted(list(sources_retrieved))
                }
            )
            logger.debug(f"Retrieval span metadata updated: num_docs={len(retrieved_docs)}, months={months_retrieved}")
        except ImportError:
            logger.debug("langfuse.decorators not available for span metadata")
        except Exception as e:
            logger.debug(f"Failed to update retrieval span metadata: {str(e)}")
        
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