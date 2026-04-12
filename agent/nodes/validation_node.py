"""Validation node to verify answer grounding and quality."""

from agent.state import AgentState
import logging

logger = logging.getLogger(__name__)


def validation_node(state: AgentState) -> AgentState:
    """Validate the generated answer for grounding and quality."""
    
    answer = state.get("answer", "")
    retrieved_docs = state.get("retrieved_docs", [])
    citations = state.get("citations", [])
    
    # Check if answer indicates lack of information
    no_info_phrases = [
        "don't have",
        "not found",
        "not available",
        "cannot find",
        "no information"
    ]
    
    has_no_info = any(phrase in answer.lower() for phrase in no_info_phrases)
    
    if has_no_info:
        state["is_grounded"] = False
        state["confidence"] = "low"
    else:
        # Check if answer has citations
        has_citations = len(citations) > 0
        
        # Check if answer contains specific data
        has_specific_data = any(char.isdigit() for char in answer)
        
        # Determine confidence
        if has_citations and has_specific_data and len(retrieved_docs) > 0:
            state["confidence"] = "high"
            state["is_grounded"] = True
        elif has_citations or has_specific_data:
            state["confidence"] = "medium"
            state["is_grounded"] = True
        else:
            state["confidence"] = "low"
            state["is_grounded"] = False
    
    # Add validation note if confidence is low
    if state["confidence"] == "low":
        state["answer"] += "\n\n(Note: This answer may not be fully grounded in the factsheet data. Please verify.)"
    
    # Record validation span metadata (Requirements 1.2, 1.3)
    try:
        from langfuse.decorators import langfuse_context
        
        # Update current observation (span) with validation metadata
        langfuse_context.update_current_observation(
            metadata={
                "is_grounded": state["is_grounded"],
                "confidence_level": state["confidence"],
                "has_citations": len(citations) > 0,
                "num_citations": len(citations),
                "citations": citations
            }
        )
        logger.debug(
            f"Validation span metadata updated: is_grounded={state['is_grounded']}, "
            f"confidence={state['confidence']}, has_citations={len(citations) > 0}"
        )
    except ImportError:
        logger.debug("langfuse.decorators not available for span metadata")
    except Exception as e:
        logger.debug(f"Failed to update validation span metadata: {str(e)}")
    
    return state