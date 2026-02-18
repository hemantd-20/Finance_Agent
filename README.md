# Financial Q&A Chatbot Agent

A LangGraph-based AI agent that answers questions about HDFC Index Fund factsheets using semantic search and intelligent query processing.

## Features

- **Clarification Handling**: Asks for clarification when queries are ambiguous
- **Intelligent Query Classification**: Automatically detects intra-document vs inter-document queries
- **Semantic Search**: Uses MongoDB Atlas Vector Search with BGE-M3 embeddings
- **Strict Grounding**: Prevents hallucinations by answering only from factsheet data
- **Citation Tracking**: Provides source attribution for all answers
- **Interactive UI**: Clean Streamlit interface for easy interaction

## Project Structure

```
Finance_Agent/
├── app.py                          # Streamlit interface
├── setup_database.py               # Database initialization script
├── config.py                       # Configuration
├── requirements.txt                # Dependencies
├── .env                            # Environment variables
├── agent/
│   ├── graph.py                    # LangGraph workflow
│   ├── state.py                    # State schema
│   └── nodes/
│       ├── clarification_node.py   # Handles ambiguous queries
│       ├── classifier_node.py      # Classifies query type
│       ├── retrieval_node.py       # Retrieves relevant documents
│       ├── generation_node.py      # Generates answers
│       └── validation_node.py      # Validates and adds citations
├── utils/
│   ├── document_processor.py       # PDF processing and chunking
│   ├── embeddings.py               # BGE-M3 embedding generation
│   └── mongodb_handler.py          # MongoDB operations
└── data/
    └── raw/                        # PDF factsheets
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- Google AI API Key (Gemini)
- MongoDB Atlas account with Vector Search enabled

### 2. Installation

```bash
# Navigate to project directory
cd Finance_Agent

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root with your credentials:

```
GOOGLE_API_KEY=your_google_api_key_here
MONGODB_URI=your_mongodb_atlas_uri_here
MONGODB_DB_NAME=financial_qa_db
MONGODB_COLLECTION_NAME=factsheet_embeddings
```

### 4. MongoDB Atlas Vector Search Index Setup

**IMPORTANT**: You must create a vector search index in MongoDB Atlas before running the application.

1. Go to MongoDB Atlas Dashboard
2. Select your cluster → Browse Collections
3. Select your database and collection
4. Go to "Search Indexes" tab
5. Click "Create Search Index"
6. Choose "JSON Editor" and paste:

```json
{
  "name": "vector_index_1",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 1024,
        "similarity": "cosine"
      },
      {
        "type": "filter",
        "path": "month"
      },
      {
        "type": "filter",
        "path": "fund_name"
      }
    ]
  }
}
```

### 5. Add Factsheet PDFs

Place HDFC Index Fund factsheets in `data/raw/` directory. The system currently includes:
- October 2025
- November 2025  
- December 2025

### 6. Initialize Database

Process PDFs and populate MongoDB:

```bash
python setup_database.py
```

This will:
- Extract text from PDFs
- Create chunks with metadata
- Generate embeddings
- Upload to MongoDB Atlas

### 7. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage Examples

### Sample Questions

**Intra-document (Single Month):**
- "Who is the Fund Manager for October 2025?"
- "What is the NAV in November?"
- "What was the AUM for December 2025?"

**Inter-document (Multiple Months):**
- "How is the NAV trend across October to December?"
- "Compare the portfolio turnover across the three months"
- "What is the performance trend from October to December?"

### Query Types

- **Intra-doc**: Queries about a single month
- **Inter-doc**: Queries comparing multiple months

### Confidence Levels

- **High**: Answer with citations and specific data
- **Medium**: Answer with partial grounding
- **Low**: Limited information available

## Technical Details

### Models Used

- **Embeddings**: BGE-M3 (1024 dimensions, multilingual, local)
- **Classification**: Gemini 2.5 Flash (fast, cost-effective)
- **Generation**: Gemini 2.5 Flash (accurate, grounded responses)

### Key Features

1. **Metadata Filtering**: Efficiently retrieves relevant months
2. **Semantic Search**: Understands query intent beyond keywords
3. **Hallucination Prevention**: Strict grounding in source documents
4. **Citation Tracking**: Transparent source attribution
5. **Ambiguity Handling**: Asks clarifying questions when needed

### LangGraph Workflow

The agent uses a state-based workflow:

1. **Clarification Node**: Checks if query needs clarification
2. **Classifier Node**: Determines query type (intra/inter)
3. **Retrieval Node**: Performs semantic search with filters
4. **Generation Node**: Creates grounded answer with citations
5. **Validation Node**: Verifies answer quality and confidence

## Troubleshooting

### Common Issues

1. **No documents retrieved**
   - Verify MongoDB Vector Search index `vector_index_1` is created
   - Check if PDFs were processed correctly with `setup_database.py`
   - Ensure embedding dimensions match (1024 for BGE-M3)

2. **API errors**
   - Verify `GOOGLE_API_KEY` is valid
   - Check API quota limits

3. **MongoDB connection errors**
   - Verify `MONGODB_URI` is correct
   - Check MongoDB Atlas network access settings
   - Ensure cluster is running

## Technology Stack

- **LangGraph**: Agent workflow orchestration
- **Gemini 2.5 Flash**: Query classification and answer generation
- **BGE-M3**: Local multilingual embeddings (1024 dimensions)
- **MongoDB Atlas**: Vector database with semantic search
- **Streamlit**: Web interface
- **PDFPlumber**: PDF text extraction

## License

MIT License
