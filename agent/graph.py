"""LangGraph workflow for the Financial Q&A Agent."""

from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.clarification_node import clarification_node
from agent.nodes.classifier_node import classifier_node
from agent.nodes.retrieval_node import retrieval_node
from agent.nodes.generation_node import generation_node
from agent.nodes.validation_node import validation_node


def create_agent_graph():
    """Create and compile the LangGraph workflow."""
    
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("classifier", classifier_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("generation", generation_node)
    workflow.add_node("validation", validation_node)
    
    # Define the workflow edges
    workflow.set_entry_point("clarification")
    
    # Conditional edge from clarification
    def should_clarify(state):
        if state.get("needs_clarification", False):
            return "clarify"
        return "classify"
    
    workflow.add_conditional_edges(
        "clarification",
        should_clarify,
        {
            "clarify": END,  # End if clarification needed
            "classify": "classifier"
        }
    )
    
    # Linear flow after classification
    workflow.add_edge("classifier", "retrieval")
    workflow.add_edge("retrieval", "generation")
    workflow.add_edge("generation", "validation")
    workflow.add_edge("validation", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


class FinancialQAAgent:
    """Main agent class for handling queries."""
    
    def __init__(self):
        self.app = create_agent_graph()
    
    def query(self, user_query: str) -> dict:
        """Process a user query and return the response."""
        
        # Initialize state
        initial_state = {
            "query": user_query,
            "query_type": None,
            "months_mentioned": None,
            "needs_clarification": False,
            "clarification_question": None,
            "retrieved_docs": None,
            "answer": "",
            "citations": None,
            "is_grounded": False,
            "confidence": None,
            "error": None
        }
        
        # Run the workflow
        final_state = self.app.invoke(initial_state)
        
        # Prepare response
        response = {
            "answer": final_state.get("answer", ""),
            "citations": final_state.get("citations", []),
            "confidence": final_state.get("confidence", "unknown"),
            "query_type": final_state.get("query_type", "unknown")
        }
        
        # Handle clarification case
        if final_state.get("needs_clarification", False):
            response["answer"] = final_state.get("clarification_question", "")
            response["needs_clarification"] = True
        else:
            response["needs_clarification"] = False
        
        # Handle errors
        if final_state.get("error"):
            response["error"] = final_state["error"]
        
        return response
    
    def visualize_graph(self, output_path: str = "agent_graph.png"):
        """Visualize the agent graph (requires graphviz)."""
        try:
            from IPython.display import Image, display
            img = Image(self.app.get_graph().draw_png())
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(img.data)
            
            print(f"Graph saved to {output_path}")
            return img
        except Exception as e:
            print(f"Could not visualize graph: {e}")
            print("Install graphviz: pip install graphviz")