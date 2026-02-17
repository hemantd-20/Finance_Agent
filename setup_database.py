"""Script to process PDFs and populate MongoDB Atlas vector store."""

import os
from utils.document_processor import DocumentProcessor
from utils.mongodb_handler import MongoDBHandler


def setup_database(pdf_directory: str = "data/raw"):
    """Process PDFs and add them to MongoDB Atlas."""
    
    print("=" * 50)
    print("Financial Q&A Agent - Database Setup")
    print("=" * 50)
    
    # Initialize components
    processor = DocumentProcessor()
    mongodb_handler = MongoDBHandler()
    
    # Get PDF files
    pdf_files = [
        os.path.join(pdf_directory, f) 
        for f in os.listdir(pdf_directory) 
        if f.endswith('.pdf')
    ]
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_directory}")
        print("Please add HDFC Index Fund factsheets (Oct, Nov, Dec) to data/raw/")
        return
    
    print(f"\nFound {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"  - {os.path.basename(pdf)}")
    
    # Process PDFs
    print("\nProcessing PDFs...")
    all_documents = processor.process_multiple_pdfs(pdf_files)
    
    if not all_documents:
        print("No documents were created. Please check your PDF files.")
        return
    
    print(f"\nTotal documents created: {len(all_documents)}")
    
    # Clear existing data (optional)
    print("\nClearing existing data from MongoDB...")
    mongodb_handler.delete_all_documents()
    
    # Add documents to MongoDB
    print("\nAdding documents to MongoDB Atlas...")
    mongodb_handler.add_documents(all_documents)
    
    print("\n" + "=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print("\nIMPORTANT: Make sure you have created the vector search index in MongoDB Atlas.")
    print("Index configuration:")
    print("""
{
  "name": "vector_index_1",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 3072,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "metadata.month"
      },
      {
        "type": "filter",
        "path": "metadata.fund_name"
      }
    ]
  }
}
    """)
    
    # Close connection
    mongodb_handler.close()


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    # os.makedirs("data/raw", exist_ok=True)
    
    setup_database()