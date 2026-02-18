"""Test if metadata is being stored correctly."""

from langchain_core.documents import Document
from utils.mongodb_handler import MongoDBHandler
from pymongo import MongoClient
import config

def test_metadata():
    """Test metadata storage."""
    
    print("=" * 60)
    print("TESTING METADATA STORAGE")
    print("=" * 60)
    
    # Create a test document with metadata
    test_doc = Document(
        page_content="This is a test document for October 2025.",
        metadata={
            "source": "test.pdf",
            "fund_name": "Test Fund",
            "month": "October",
            "year": "2025",
            "chunk_id": 0
        }
    )
    
    print("\n1. Test document created:")
    print(f"   Content: {test_doc.page_content}")
    print(f"   Metadata: {test_doc.metadata}")
    
    # Add to MongoDB
    print("\n2. Adding test document to MongoDB...")
    mongodb_handler = MongoDBHandler()
    
    try:
        mongodb_handler.vector_store.add_documents([test_doc])
        print("   ✓ Document added")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # Check what was actually stored
    print("\n3. Checking what was stored in MongoDB...")
    client = MongoClient(config.MONGODB_URI)
    db = client[config.MONGODB_DB_NAME]
    collection = db[config.MONGODB_COLLECTION_NAME]
    
    # Find the test document
    stored_doc = collection.find_one({"text": "This is a test document for October 2025."})
    
    if stored_doc:
        print("   ✓ Document found in MongoDB")
        print(f"   - Has 'text' field: {'text' in stored_doc}")
        print(f"   - Has 'embedding' field: {'embedding' in stored_doc}")
        print(f"   - Has 'metadata' field: {'metadata' in stored_doc}")
        
        if 'metadata' in stored_doc:
            print(f"   - Metadata content: {stored_doc['metadata']}")
        else:
            print("   ✗ NO METADATA FIELD!")
            print(f"   - All fields: {list(stored_doc.keys())}")
    else:
        print("   ✗ Document not found!")
    
    # Clean up - delete test document
    print("\n4. Cleaning up test document...")
    collection.delete_one({"text": "This is a test document for October 2025."})
    print("   ✓ Test document deleted")
    
    client.close()
    mongodb_handler.close()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_metadata()
