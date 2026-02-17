# Financial Q&A Chatbot Agent

A LangGraph-based AI agent that answers questions about HDFC Index Fund factsheets.

## Features

- **Clarification Handling**: Asks for clarification when queries are ambiguous
- **Intelligent Query Classification**: Automatically detects intra-document vs inter-document queries
- **Semantic Search**: Uses MongoDB Atlas Vector Search for accurate retrieval
- **Strict Grounding**: Prevents hallucinations by answering only from factsheet data
- **Citation Tracking**: Provides source attribution for all answers
- **Interactive UI**: Clean Streamlit interface for easy interaction

## Architecture

```
User Query
    ↓
Clarification Check → [Ambiguous?] → Ask Question
    ↓ [Clear]
Query Classifier (Gemini 2.0 Flash Lite)
    ↓
MongoDB Vector Search + Metadata Filtering
    ↓
Answer Generation (Gemini 2.0 Flash)
    ↓
Validation & Citation
    ↓
Final Answer
```

## Project Structure

```
financial-qa-chatbot/
├── app.py                          # Streamlit interface
├── setup_database.py               # Database initialization script
├── config.py                       # Configuration
├── requirements.txt                # Dependencies
├── .env.example                    # Environment variables template
├── agent/
│   ├── graph.py                    # LangGraph workflow
│   ├── state.py                    # State schema
│   └── nodes/
│       ├── clarification_node.py
│       ├── classifier_node.py
│       ├── retrieval_node.py
│       ├── generation_node.py
│       └── validation_node.py
├── utils/
│   ├── document_processor.py       # PDF processing
│   ├── embeddings.py               # Embedding generation
│   └── mongodb_handler.py          # MongoDB operations
└── data/
    └── raw/                        # PDF factsheets (Oct, Nov, Dec)
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- Google AI API Key (Gemini)
- MongoDB Atlas account with Vector Search enabled

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd financial-qa-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

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
  "name": "vector_index",
  "type": "vectorSearch",
  "definition": {
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 768,`
        
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
```

### 5. Add Factsheet PDFs

Download HDFC Index Fund factsheets for October, November, and December 2024 from:
https://www.hdfcfund.com/investor-services/factsheets

Place them in `data/raw/` directory:

```
data/
└── raw/
    ├── HDFC_Index_Fund_October_2024.pdf
    ├── HDFC_Index_Fund_November_2024.pdf
    └── HDFC_Index_Fund_December_2024.pdf
```

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
- "Who is the Fund Manager for October 2024?"
- "What is the NAV in November?"
- "What was the AUM for December 2024?"

**Inter-document (Multiple Months):**
- "How is the NAV trend across October to December?"
- "Compare the portfolio turnover across the three months"
- "What is the performance trend from October to December?"

### Query Types

- **🔵 Intra-doc**: Queries about a single month
- **🟢 Inter-doc**: Queries comparing multiple months

### Confidence Levels

- **High**: Answer with citations and specific data
- **Medium**: Answer with partial grounding
- **Low**: Limited information available

## Technical Details

### Models Used

- **Embeddings**: Google `text-embedding-004` (768 dimensions)
- **Classification**: Gemini 2.0 Flash Lite (fast, cost-effective)
- **Generation**: Gemini 2.0 Flash (accurate, grounded responses)

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
   - Verify MongoDB Vector Search index is created
   - Check if PDFs were processed correctly
   - Ensure embedding dimensions match (768)

2. **API errors**
   - Verify `GOOGLE_API_KEY` is valid
   - Check API quota limits
   - Ensure stable internet connection

3. **Import errors**
   - Reinstall dependencies: `pip install -r requirements.txt`
   - Check Python version (3.9+)

4. **MongoDB connection errors**
   - Verify `MONGODB_URI` is correct
   - Check MongoDB Atlas network access settings
   - Ensure cluster is running

## Project Constraints

- Simple and clean implementation
- No unnecessary features
- Separation of logic (agent) and UI (Streamlit)
- Focus on accuracy and avoiding hallucinations
- Free tier compatible (Gemini API)

## Future Enhancements

- Add more fund factsheets
- Support for different fund types
- Historical trend analysis
- PDF export of answers
- Multi-turn conversation memory

## License

MIT License

## Author

Built as a Financial Q&A Agent using LangGraph and Gemini API.

## Output: python setup_database.py
==================================================
Financial Q&A Agent - Database Setup
==================================================

Found 3 PDF files:
  - HDFC-MF-Index-Solutions-Factsheet-December-2025_0.pdf
  - HDFC-MF-Index-Solutions-Factsheet-November-2025_1.pdf
  - HDFC-MF-Index-Solutions-Factsheet-October-2025.pdf

Processing PDFs...
Processed data/raw\HDFC-MF-Index-Solutions-Factsheet-December-2025_0.pdf: 603 chunks created
Processed data/raw\HDFC-MF-Index-Solutions-Factsheet-November-2025_1.pdf: 470 chunks created
Processed data/raw\HDFC-MF-Index-Solutions-Factsheet-October-2025.pdf: 454 chunks created
Total documents created: 1527

Total documents created: 1527

Clearing existing data from MongoDB...
All documents deleted from MongoDB Atlas

Adding documents to MongoDB Atlas...
Successfully added 1527 documents to MongoDB Atlas

==================================================
Setup Complete!
==================================================

IMPORTANT: Make sure you have created the vector search index in MongoDB Atlas.  
Index configuration:

{
  "name": "vector_index",
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