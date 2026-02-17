"""Clarification node to check if query needs clarification."""

from agent.state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
import config


def clarification_node(state: AgentState) -> AgentState:
    """Check if the query is clear or needs clarification."""
    
    query = state["query"]
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model=config.CLASSIFIER_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=0
    )
    
    # Prompt to check if clarification is needed
    prompt = f"""You are a financial assistant analyzing user queries about HDFC Index Fund factsheets.

Available factsheet months: October 2024, November 2024, December 2024

Analyze this query and determine if it's clear enough to answer or needs clarification:
Query: "{query}"

Rules:
1. If the query is clear and answerable with factsheet data, respond: CLEAR
2. If the query is ambiguous or missing critical information, respond: AMBIGUOUS
3. If AMBIGUOUS, provide a brief clarification question

Examples:
- "Who is the fund manager?" → CLEAR (we have this for all months)
- "What is the NAV?" → AMBIGUOUS (which month?)
- "NAV trend" → CLEAR (implies across months)
- "Tell me about the fund" → AMBIGUOUS (too vague)

Respond in this format:
STATUS: [CLEAR/AMBIGUOUS]
CLARIFICATION: [question if ambiguous, else empty]

Your analysis:"""
    
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