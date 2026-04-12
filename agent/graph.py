"""LangGraph workflow for the Financial Q&A Agent."""

import asyncio
import logging
from typing import Optional
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.clarification_node import clarification_node
from agent.nodes.classifier_node import classifier_node
from agent.nodes.retrieval_node import retrieval_node
from agent.nodes.generation_node import generation_node
from agent.nodes.validation_node import validation_node
from config import get_langfuse_handler, get_langfuse_client
from evaluation.ragas_evaluator import RagasEvaluator

logger = logging.getLogger(__name__)


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
        # Initialize Langfuse handler for tracing (Requirement 1.1)
        self.langfuse_handler = get_langfuse_handler()
        if self.langfuse_handler:
            logger.info("Langfuse tracing enabled for FinancialQAAgent")
        else:
            logger.info("Langfuse tracing disabled")
        
        # Initialize Ragas evaluator (Requirement 6.1, 6.2, 6.3, 6.4, 6.5)
        langfuse_client = get_langfuse_client()
        self.ragas_evaluator = RagasEvaluator(langfuse_client)
        logger.info("Ragas evaluator initialized")
    
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
        
        # Prepare config with callback handler (Requirement 1.1, 1.5)
        config = {}
        if self.langfuse_handler:
            config["callbacks"] = [self.langfuse_handler]
        
        # Run the workflow
        final_state = self.app.invoke(initial_state, config=config)
        
        # Add trace metadata tagging (Requirements 10.1, 10.2, 10.3)
        if self.langfuse_handler:
            try:
                from langfuse.decorators import langfuse_context
                
                # Extract metadata from final state
                query_type = final_state.get("query_type", "unknown")
                confidence = final_state.get("confidence", "unknown")
                months_mentioned = final_state.get("months_mentioned", [])
                is_grounded = final_state.get("is_grounded", False)
                retrieved_docs = final_state.get("retrieved_docs", [])
                citations = final_state.get("citations", [])
                
                # Create trace tags (Requirements 10.1, 10.2, 10.3)
                tags = [
                    f"query_type:{query_type}",
                    f"confidence:{confidence}"
                ]
                if months_mentioned:
                    months_str = ",".join(months_mentioned) if isinstance(months_mentioned, list) else str(months_mentioned)
                    tags.append(f"months:{months_str}")
                
                # Create metadata dict
                metadata = {
                    "query": user_query,
                    "query_type": query_type,
                    "months_mentioned": months_mentioned,
                    "confidence": confidence,
                    "is_grounded": is_grounded,
                    "num_retrieved_docs": len(retrieved_docs) if retrieved_docs else 0,
                    "citations": citations if citations else []
                }
                
                # Set trace name and metadata
                langfuse_context.update_current_trace(
                    name=f"FinancialQA: {query_type}",
                    tags=tags,
                    metadata=metadata
                )
                
                logger.debug(f"Trace metadata updated: tags={tags}, metadata={metadata}")
                
                # Trigger Ragas evaluation asynchronously (Requirement 6.1, 6.2, 6.3, 6.4, 6.5)
                # Extract trace ID from context
                try:
                    current_trace = langfuse_context.get_current_trace()
                    if current_trace and hasattr(current_trace, 'id'):
                        trace_id = current_trace.id
                        
                        # Extract contexts from retrieved documents
                        contexts = []
                        if retrieved_docs:
                            contexts = [
                                doc.page_content for doc in retrieved_docs
                                if hasattr(doc, 'page_content')
                            ]
                        
                        # Extract answer
                        answer = final_state.get("answer", "")
                        
                        # Trigger evaluation asynchronously (don't block response)
                        if contexts and answer and not final_state.get("needs_clarification", False):
                            asyncio.create_task(
                                self.ragas_evaluator.evaluate_trace(
                                    trace_id,
                                    user_query,
                                    contexts,
                                    answer
                                )
                            )
                            logger.debug(f"Triggered async Ragas evaluation for trace {trace_id}")
                
                except Exception as e:
                    logger.debug(f"Could not trigger Ragas evaluation: {str(e)}")
                
            except ImportError:
                logger.warning("langfuse.decorators not available for trace metadata tagging")
            except Exception as e:
                logger.warning(f"Failed to update trace metadata: {str(e)}")
        
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