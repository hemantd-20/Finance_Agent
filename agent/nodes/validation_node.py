"""Validation node to verify answer grounding and quality."""

from agent.state import AgentState


def validation_node(state: AgentState) -> AgentState:
    """Validate the generated answer for grounding and quality."""
    
    answer = state.get("answer", "")
    retrieved_docs = state.get("retrieved_docs", [])
    
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
        return state
    
    # Check if answer has citations
    has_citations = len(state.get("citations", [])) > 0
    
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
    
    return state