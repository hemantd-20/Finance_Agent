"""Generation node for creating answers with strict grounding."""

from agent.state import AgentState
from agent.prompts.prompt_loader import prompt_registry
from langchain_google_genai import ChatGoogleGenerativeAI
import config


def generation_node(state: AgentState) -> AgentState:
    """Generate answer from retrieved documents with strict grounding."""
    
    query = state["query"]
    retrieved_docs = state.get("retrieved_docs", [])
    
    # Check if we have retrieved documents
    if not retrieved_docs:
        state["answer"] = "I don't have enough information in the factsheets to answer this question."
        state["is_grounded"] = False
        state["citations"] = []
        return state
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model=config.GENERATION_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=0
    )
    
    # Prepare context from retrieved documents
    context_parts = []
    for i, doc in enumerate(retrieved_docs):
        month = doc.metadata.get("month", "Unknown")
        source = doc.metadata.get("source", "Unknown")
        year = doc.metadata.get("year", "2025")
        context_parts.append(
            f"[Document {i+1} - {month} {year} Factsheet]\n{doc.page_content}\n"
        )
    
    context = "\n".join(context_parts)
    
    # Load generation prompt from registry
    prompt = prompt_registry.format_prompt("generation_prompt", context=context, query=query)
    
    try:
        response = llm.invoke(prompt)
        answer = response.content.strip()
        
        # Extract citations (months mentioned in answer)
        citations = []
        months = ["October", "November", "December"]
        for month in months:
            if month in answer:
                # Get year from retrieved docs for this month
                year = "2025"  # Default
                for doc in retrieved_docs:
                    if doc.metadata.get("month") == month:
                        year = doc.metadata.get("year", "2025")
                        break
                citations.append(f"{month} {year}")
        
        state["answer"] = answer
        state["citations"] = citations
        state["is_grounded"] = True
        
    except Exception as e:
        print(f"Error in generation node: {e}")
        state["answer"] = "I encountered an error while generating the answer. Please try again."
        state["is_grounded"] = False
        state["citations"] = []
        state["error"] = f"Generation error: {str(e)}"
    
    return state