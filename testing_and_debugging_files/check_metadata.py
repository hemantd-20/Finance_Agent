"""Check what metadata values are actually stored in MongoDB."""

from pymongo import MongoClient
import config

def check_metadata():
    """Check actual metadata values in MongoDB."""
    
    client = MongoClient(config.MONGODB_URI)
    db = client[config.MONGODB_DB_NAME]
    collection = db[config.MONGODB_COLLECTION_NAME]
    
    print("=" * 60)
    print("CHECKING ACTUAL METADATA VALUES")
    print("=" * 60)
    
    # Get a few sample documents
    samples = list(collection.find().limit(5))
    
    print(f"\nTotal documents: {collection.count_documents({})}")
    print(f"\nSample documents metadata:\n")
    
    for i, doc in enumerate(samples, 1):
        print(f"Document {i}:")
        print(f"  - _id: {doc.get('_id')}")
        print(f"  - text preview: {doc.get('text', '')[:100]}...")
        
        metadata = doc.get('metadata', {})
        print(f"  - metadata keys: {list(metadata.keys())}")
        print(f"  - month: '{metadata.get('month')}'")
        print(f"  - year: '{metadata.get('year')}'")
        print(f"  - source: '{metadata.get('source')}'")
        print()
    
    # Get unique month values
    print("\nUnique month values in database:")
    unique_months = collection.distinct('metadata.month')
    print(f"  {unique_months}")
    
    print("\nUnique year values in database:")
    unique_years = collection.distinct('metadata.year')
    print(f"  {unique_years}")
    
    # Test filter
    print("\n" + "=" * 60)
    print("TESTING FILTERS")
    print("=" * 60)
    
    test_filters = [
        {'metadata.month': 'October'},
        {'metadata.month': 'November'},
        {'metadata.month': 'December'},
        {'metadata.month': {'$in': ['October', 'November', 'December']}},
    ]
    
    for filter_dict in test_filters:
        count = collection.count_documents(filter_dict)
        print(f"\nFilter: {filter_dict}")
        print(f"  → Matching documents: {count}")
    
    client.close()

if __name__ == "__main__":
    check_metadata()
