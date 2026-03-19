"""Classifier node to determine query type and extract months."""

from agent.state import AgentState
from agent.prompts.prompt_loader import prompt_registry
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
    
    # Load classification prompt from registry
    prompt = prompt_registry.format_prompt("classifier_prompt", query=query)
    
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