"""State schema for the LangGraph agent."""

from typing import TypedDict, List, Optional, Literal
from langchain_core.documents import Document


class AgentState(TypedDict):
    """State schema for the financial Q&A agent workflow."""
    
    # User input
    query: str
    
    # Classification results
    query_type: Optional[Literal["intra", "inter", "ambiguous"]]
    months_mentioned: Optional[List[str]]
    
    # Clarification handling
    needs_clarification: bool
    clarification_question: Optional[str]
    
    # Retrieved documents
    retrieved_docs: Optional[List[Document]]
    
    # Generation results
    answer: str
    citations: Optional[List[str]]
    
    # Validation
    is_grounded: bool
    confidence: Optional[str]
    
    # Metadata
    error: Optional[str]