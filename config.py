"""Configuration file for the Financial Q&A Chatbot Agent."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

# MongoDB Configuration
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "financial_qa_db")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "factsheet_embeddings")

# Model Configuration
EMBEDDING_MODEL = "BAAI/bge-m3"  # BGE-M3: 1024 dimensions, multilingual, local
CLASSIFIER_MODEL = "gemini-2.5-flash"  # Fast model for classification
GENERATION_MODEL = "gemini-2.5-flash"  # Main generation model

# Document Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval Configuration
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7

# Validation
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")