"""Diagnostic script to check vector search setup."""

from pymongo import MongoClient
import config
from utils.embeddings import EmbeddingHandler

def diagnose():
    """Check MongoDB setup and vector search."""
    
    print("=" * 60)
    print("VECTOR SEARCH DIAGNOSTIC")
    print("=" * 60)
    
    # 1. Check MongoDB connection and documents
    print("\n1. Checking MongoDB connection...")
    client = MongoClient(config.MONGODB_URI)
    db = client[config.MONGODB_DB_NAME]
    collection = db[config.MONGODB_COLLECTION_NAME]
    
    doc_count = collection.count_documents({})
    print(f"   ✓ Connected to MongoDB")
    print(f"   ✓ Documents in collection: {doc_count}")
    
    if doc_count == 0:
        print("   ✗ ERROR: No documents in collection!")
        print("   → Run: python setup_database.py")
        return
    
    # 2. Check sample document structure
    print("\n2. Checking document structure...")
    sample_doc = collection.find_one()
    
    if sample_doc:
        print(f"   ✓ Sample document found")
        print(f"   - Has 'text' field: {'text' in sample_doc}")
        print(f"   - Has 'embedding' field: {'embedding' in sample_doc}")
        
        if 'embedding' in sample_doc:
            embedding_dim = len(sample_doc['embedding'])
            print(f"   - Embedding dimensions: {embedding_dim}")
            
            if embedding_dim != 1024:
                print(f"   ✗ ERROR: Wrong embedding dimensions!")
                print(f"   → Expected: 1024, Got: {embedding_dim}")
                print(f"   → You need to re-run setup_database.py")
                return
            else:
                print(f"   ✓ Correct embedding dimensions (1024)")
        else:
            print("   ✗ ERROR: No embedding field in document!")
            return
    
    # 3. Check vector search indexes
    print("\n3. Checking vector search indexes...")
    indexes = list(collection.list_search_indexes())
    
    if not indexes:
        print("   ✗ ERROR: No vector search indexes found!")
        print("   → You must create a vector search index in MongoDB Atlas")
        print("   → Index name: 'vector_index_1'")
        print("   → Dimensions: 1024")
        print("   → See MIGRATION_TO_BGE_M3.md for instructions")
        return
    
    print(f"   ✓ Found {len(indexes)} search index(es)")
    
    for idx in indexes:
        print(f"\n   Index: {idx.get('name', 'unnamed')}")
        print(f"   - Status: {idx.get('status', 'unknown')}")
        
        # Check if it's the right index
        if idx.get('name') == 'vector_index_1':
            print(f"   ✓ Found 'vector_index_1' index")
            
            # Try to check dimensions (if available in index definition)
            definition = idx.get('latestDefinition', {})
            fields = definition.get('fields', [])
            
            for field in fields:
                if field.get('type') == 'vector':
                    dims = field.get('numDimensions')
                    print(f"   - Vector dimensions: {dims}")
                    
                    if dims != 1024:
                        print(f"   ✗ ERROR: Index has wrong dimensions!")
                        print(f"   → Expected: 1024, Got: {dims}")
                        print(f"   → You must UPDATE the index in MongoDB Atlas")
                        print(f"   → See MIGRATION_TO_BGE_M3.md for instructions")
                        return
                    else:
                        print(f"   ✓ Correct index dimensions (1024)")
    
    # 4. Test embedding generation
    print("\n4. Testing embedding generation...")
    try:
        embedding_handler = EmbeddingHandler()
        test_text = "What is the NAV of HDFC Index Fund?"
        embedding = embedding_handler.generate_embedding(test_text)
        
        print(f"   ✓ Embedding generated successfully")
        print(f"   - Embedding dimensions: {len(embedding)}")
        
        if len(embedding) != 1024:
            print(f"   ✗ ERROR: Generated embedding has wrong dimensions!")
            return
    except Exception as e:
        print(f"   ✗ ERROR generating embedding: {e}")
        return
    
    # 5. Test vector search
    print("\n5. Testing vector search...")
    try:
        from utils.mongodb_handler import MongoDBHandler
        
        mongodb_handler = MongoDBHandler()
        results = mongodb_handler.similarity_search(
            query="What is the NAV?",
            k=3
        )
        
        print(f"   ✓ Vector search executed")
        print(f"   - Results found: {len(results)}")
        
        if len(results) == 0:
            print(f"   ✗ WARNING: No results returned!")
            print(f"   → Possible causes:")
            print(f"      1. Vector index not ready (wait a few minutes)")
            print(f"      2. Index dimensions mismatch")
            print(f"      3. Index not properly configured")
        else:
            print(f"   ✓ Vector search working!")
            print(f"\n   Sample result:")
            print(f"   {results[0].page_content[:200]}...")
            
    except Exception as e:
        print(f"   ✗ ERROR during vector search: {e}")
        return
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    diagnose()
