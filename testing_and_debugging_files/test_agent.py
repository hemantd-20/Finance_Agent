"""Test script for the Financial Q&A Agent."""

from agent.graph import FinancialQAAgent


def test_agent():
    """Test the agent with sample queries."""
    
    print("=" * 70)
    print("Financial Q&A Agent - Test Script")
    print("=" * 70)
    
    # Initialize agent
    print("\nInitializing agent...")
    agent = FinancialQAAgent()
    print("Agent initialized successfully!\n")
    
    # Test queries
    test_queries = [
        "Who is the Fund Manager for HDFC Index fund in October 2025?",
        "What is the NAV trend from October to December 2025?",
        "Compare the AUM across the three months",
        "What was the portfolio turnover ratio in November 2025?",
        "Tell me about the performance",  # Ambiguous - should ask for clarification
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 70}")
        print(f"Test Query {i}: {query}")
        print("=" * 70)
        
        try:
            response = agent.query(query)
            
            print(f"\nQuery Type: {response.get('query_type', 'unknown')}")
            print(f"Confidence: {response.get('confidence', 'unknown')}")
            
            if response.get('needs_clarification'):
                print(f"\n⚠️  CLARIFICATION NEEDED:")
                print(f"{response['answer']}")
            else:
                print(f"\nAnswer:")
                print(f"{response['answer']}")
                
                if response.get('citations'):
                    print(f"\nCitations: {', '.join(response['citations'])}")
            
            if response.get('error'):
                print(f"\n⚠️  Error: {response['error']}")
        
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")
    
    print(f"\n{'=' * 70}")
    print("Testing complete!")
    print("=" * 70)


if __name__ == "__main__":
    test_agent()