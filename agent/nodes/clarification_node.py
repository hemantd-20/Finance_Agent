"""Clarification node to check if query needs clarification."""

from agent.state import AgentState
from agent.prompts.prompt_loader import prompt_registry
from langchain_groq import ChatGroq
import config


def clarification_node(state: AgentState) -> AgentState:
    """Check if the query is clear or needs clarification."""
    
    query = state["query"]
    
    # Initialize LLM
    llm = ChatGroq(
        model=config.CLASSIFIER_MODEL,
        groq_api_key=config.GROQ_API_KEY,
        temperature=0
    )
    
    # Load clarification prompt from registry
    prompt = prompt_registry.format_prompt("clarification_prompt", query=query)
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Parse response
        lines = response_text.split("\n")
        status_line = [l for l in lines if l.startswith("STATUS:")][0]
        status = status_line.split(":")[1].strip()
        
        if status == "AMBIGUOUS":
            clarification_line = [l for l in lines if l.startswith("CLARIFICATION:")][0]
            clarification = clarification_line.split(":", 1)[1].strip()
            
            state["needs_clarification"] = True
            state["clarification_question"] = clarification
        else:
            state["needs_clarification"] = False
            state["clarification_question"] = None
    
    except Exception as e:
        print(f"Error in clarification node: {e}")
        # Default to not needing clarification on error
        state["needs_clarification"] = False
        state["clarification_question"] = None
    
    return state