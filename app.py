"""Streamlit app for Financial Q&A Chatbot Agent."""

import streamlit as st
from agent.graph import FinancialQAAgent
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = None


def initialize_agent():
    """Initialize the agent."""
    if st.session_state.agent is None:
        try:
            with st.spinner("Initializing agent..."):
                st.session_state.agent = FinancialQAAgent()
            st.success("Agent initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing agent: {e}")
            st.stop()


def main():
    """Main Streamlit app."""
    
    # Page configuration
    st.set_page_config(
        page_title="Financial Q&A Chatbot",
        page_icon="💰",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("💰 Financial Q&A Agent")
        st.markdown("---")
        
        st.markdown("""
        ### About
        This chatbot answers questions about HDFC Index Fund factsheets.
        
        **Available Data:**
        - October 2024
        - November 2024
        - December 2024
        
        ### Sample Questions:
        - Who is the Fund Manager for October 2024?
        - What is the NAV trend from October to December?
        - Compare the AUM across the three months
        - What was the portfolio turnover in November?
        """)
        
        st.markdown("---")
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Query Type Legend:**")
        st.markdown("🔵 Intra-doc: Single month")
        st.markdown("🟢 Inter-doc: Multiple months")
        
    # Main content
    st.title("💬 Financial Q&A Chatbot")
    st.markdown("Ask questions about HDFC Index Fund factsheets")
    
    # Initialize agent
    initialize_agent()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display metadata for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    query_type = metadata.get("query_type", "unknown")
                    icon = "🔵" if query_type == "intra" else "🟢"
                    st.caption(f"{icon} Type: {query_type}")
                with col2:
                    confidence = metadata.get("confidence", "unknown")
                    st.caption(f"🎯 Confidence: {confidence}")
                with col3:
                    citations = metadata.get("citations", [])
                    if citations:
                        st.caption(f"📚 Sources: {', '.join(citations)}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the factsheets..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.query(prompt)
                    
                    # Display answer
                    answer = response.get("answer", "I couldn't generate an answer.")
                    st.markdown(answer)
                    
                    # Display metadata
                    if not response.get("needs_clarification", False):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            query_type = response.get("query_type", "unknown")
                            icon = "🔵" if query_type == "intra" else "🟢"
                            st.caption(f"{icon} Type: {query_type}")
                        with col2:
                            confidence = response.get("confidence", "unknown")
                            st.caption(f"🎯 Confidence: {confidence}")
                        with col3:
                            citations = response.get("citations", [])
                            if citations:
                                st.caption(f"📚 Sources: {', '.join(citations)}")
                    
                    # Handle errors
                    if "error" in response:
                        st.warning(f"⚠️ {response['error']}")
                    
                    # Add assistant message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "metadata": {
                            "query_type": response.get("query_type"),
                            "confidence": response.get("confidence"),
                            "citations": response.get("citations", [])
                        }
                    })
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            <small>Financial Q&A Agent | Built with LangGraph & Gemini API</small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()