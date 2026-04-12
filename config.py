"""Configuration file for the Financial Q&A Chatbot Agent."""

import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

# MongoDB Configuration
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "financial_qa_db")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "factsheet_embeddings")

# Langfuse Configuration
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
LANGFUSE_ENABLED = os.getenv("LANGFUSE_ENABLED", "true").lower() in ("true", "1", "yes")

# Model Configuration
EMBEDDING_MODEL = "BAAI/bge-m3"  # BGE-M3: 1024 dimensions, multilingual, local
CLASSIFIER_MODEL = "llama-3.3-70b-versatile"  # Groq Llama 3.3 70B for classification
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
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables")


def get_langfuse_client() -> Optional[object]:
    """
    Initialize and return a Langfuse client with credential validation.
    
    Returns:
        Langfuse client instance if credentials are valid, None otherwise.
    """
    if not LANGFUSE_ENABLED:
        logger.info("Langfuse is disabled via LANGFUSE_ENABLED environment variable")
        return None
    
    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        logger.warning(
            "Langfuse credentials not found. Observability features will be disabled. "
            "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables to enable."
        )
        return None
    
    try:
        from langfuse import Langfuse
        
        client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_BASE_URL
        )
        
        # Validate connection by attempting to authenticate
        client.auth_check()
        logger.info(f"Langfuse client initialized successfully (host: {LANGFUSE_BASE_URL})")
        return client
        
    except ImportError:
        logger.warning(
            "Langfuse package not installed. Install with: pip install langfuse"
        )
        return None
    except Exception as e:
        logger.warning(
            f"Failed to initialize Langfuse client: {str(e)}. "
            "Observability features will be disabled."
        )
        return None


def get_langfuse_handler() -> Optional[object]:
    """
    Initialize and return a Langfuse CallbackHandler with graceful degradation.
    
    The CallbackHandler reads credentials from environment variables:
    - LANGFUSE_PUBLIC_KEY
    - LANGFUSE_SECRET_KEY
    - LANGFUSE_BASE_URL (optional)
    
    Returns:
        CallbackHandler instance if Langfuse is available, None otherwise.
    """
    if not LANGFUSE_ENABLED:
        return None
    
    if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
        logger.warning(
            "Langfuse credentials not found. Tracing will be disabled."
        )
        return None
    
    try:
        from langfuse.langchain import CallbackHandler
        
        # CallbackHandler reads credentials from environment variables automatically
        # No need to pass them as parameters
        handler = CallbackHandler()
        
        logger.info("Langfuse CallbackHandler initialized successfully")
        return handler
        
    except ImportError:
        logger.warning(
            "Langfuse package not installed. Install with: pip install langfuse"
        )
        return None
    except Exception as e:
        logger.warning(
            f"Failed to initialize Langfuse handler: {str(e)}. "
            "Tracing will be disabled."
        )
        return None