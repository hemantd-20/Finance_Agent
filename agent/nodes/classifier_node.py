"""Classifier node to determine query type and extract months."""

from agent.state import AgentState
from langchain_groq import ChatGroq
import config
import json


def classifier_node(state: AgentState) -> AgentState:
    """Classify query as intra-doc or inter-doc and extract mentioned months."""
    
    query = state["query"]
    
    # Initialize LLM
    llm = ChatGroq(
        model=config.CLASSIFIER_MODEL,
        groq_api_key=config.GROQ_API_KEY,
        temperature=0
    )
    
    # Classification prompt
    prompt = f"""You are a query classifier for a financial Q&A system.

Available factsheet months: October 2025, November 2025, December 2025

Classify this query:
Query: "{query}"

Classification Types:
1. INTRA-DOC: Query needs data from a SINGLE month
   - Examples: "Who is fund manager in October?", "What is NAV for November?"
   
2. INTER-DOC: Query needs data from MULTIPLE months
   - Examples: "NAV trend across months", "Compare October and December", "How did performance change?"

Also extract any months mentioned in the query.

Respond in JSON format:
{{
  "query_type": "intra" or "inter",
  "months_mentioned": ["October", "November", "December"] or [],
  "reasoning": "brief explanation"
}}

Your classification:"""
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Try to parse JSON
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        print(result)
        
        state["query_type"] = result.get("query_type", "intra")
        state["months_mentioned"] = result.get("months_mentioned", [])
        
        print(f"Classification: {state['query_type']}, Months: {state['months_mentioned']}")
    
    except Exception as e:
        print(f"Error in classifier node: {e}")
        # Default to intra-doc if classification fails
        state["query_type"] = "intra"
        state["months_mentioned"] = []
    
    return state