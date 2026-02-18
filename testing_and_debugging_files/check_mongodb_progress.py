"""Quick script to check MongoDB document count."""

from pymongo import MongoClient
import config
import time

def check_progress():
    """Check how many documents are in MongoDB."""
    client = MongoClient(config.MONGODB_URI)
    db = client[config.MONGODB_DB_NAME]
    collection = db[config.MONGODB_COLLECTION_NAME]
    
    print("Checking MongoDB document count...")
    print("Press Ctrl+C to stop monitoring\n")
    
    previous_count = 0
    try:
        while True:
            count = collection.count_documents({})
            
            if count != previous_count:
                print(f"Current documents in MongoDB: {count}/1527 ({(count/1527)*100:.1f}%)")
                previous_count = count
            else:
                print(f"Current documents: {count} (no change)", end='\r')
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print(f"\n\nFinal count: {count} documents")
        client.close()

if __name__ == "__main__":
    check_progress()
