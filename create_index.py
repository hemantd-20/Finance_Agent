import os
import time
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel

class DataRetrieval:
    def __init__(self):
        self.array_of_results = []
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.collection = self.client["sample_mflix"]["rag_pdf_search"]


    def search_index_model(self):
        '''
        First check if the search index already exists, 
        if exists: 
            simply check its status(if its queryable or not)
        if not:
            create one
            For which, create the index model, then the search index.
        '''
        index_name="vector_index_1"

        # check if index already exists
        existing_indexes = list(self.collection.list_search_indexes())
        index_exists = any(idx.get("name") == index_name for idx in existing_indexes)

        if not index_exists:
            print(f"Creating index: {index_name}")
            search_index_model = SearchIndexModel(
                definition = {
                    "fields": [
                        {
                            "type": "vector",
                            "numDimensions": 3072,
                            "path": "embedding",
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
                },
                name = index_name,
                type = "vectorSearch"
            )
            self.collection.create_search_index(model=search_index_model)
        else:
            print(f"Index '{index_name} already exists. Checking status...")

        print("Polling to check if the index is ready...")
        predicate=None
        if predicate is None:
            predicate = lambda index: index.get("queryable") is True
        
        while True:
            indices = list(self.collection.list_search_indexes(index_name))
            if len(indices) and predicate(indices[0]):
                break
            time.sleep(5)
        print(index_name + "is ready for querying.")

if __name__ == "__main__":
    data_retrieval = DataRetrieval()
    data_retrieval.search_index_model()