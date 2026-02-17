"""Generation node for creating answers with strict grounding."""

from agent.state import AgentState
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
        context_parts.append(
            f"[Document {i+1} - {month} 2024 Factsheet]\n{doc.page_content}\n"
        )
    
    context = "\n".join(context_parts)
    
    # Generation prompt with strict grounding instructions
    prompt = f"""You are a financial data assistant answering questions about HDFC Index Fund factsheets.

CRITICAL RULES:
1. Answer ONLY using information from the provided context below
2. If the answer is not in the context, say "I don't have this information in the factsheets"
3. Always cite which month's factsheet you're referencing (e.g., "According to the October 2024 factsheet...")
4. For numerical data, quote EXACT values from the context
5. Never make assumptions or use general knowledge
6. Be concise and direct

CONTEXT:
{context}

USER QUERY: {query}

Your answer (with citations):"""
    
    try:
        response = llm.invoke(prompt)
        answer = response.content.strip()
        
        # Extract citations (months mentioned in answer)
        citations = []
        months = ["October", "November", "December"]
        for month in months:
            if month in answer:
                citations.append(f"{month} 2024")
        
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