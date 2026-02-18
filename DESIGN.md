# Financial Q&A Agent - System Design

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                      (Streamlit Web App)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangGraph Agent                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Clarification │→ │ Classifier   │→ │  Retrieval   │         │
│  │    Node      │  │    Node      │  │    Node      │         │
│  └──────────────┘  └──────────────┘  └──────┬───────┘         │
│                                              │                  │
│  ┌──────────────┐  ┌──────────────┐         │                  │
│  │  Validation  │← │  Generation  │←────────┘                  │
│  │    Node      │  │    Node      │                            │
│  └──────────────┘  └──────────────┘                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
    ┌───────────────────┐     ┌───────────────────┐
    │   Gemini 2.5      │     │  MongoDB Atlas    │
    │   Flash API       │     │  Vector Search    │
    │                   │     │                   │
    │ • Classification  │     │ • BGE-M3 Vectors  │
    │ • Generation      │     │ • Metadata Filter │
    └───────────────────┘     └───────────────────┘
```

## System Components

### 1. User Interface Layer
- **Technology**: Streamlit
- **Purpose**: Provides chat interface for user interaction
- **Features**:
  - Chat history management
  - Query type indicators (intra/inter-document)
  - Confidence level display
  - Citation tracking

### 2. Agent Orchestration Layer
- **Technology**: LangGraph
- **Purpose**: Manages workflow state and node transitions
- **State Management**: Tracks query, classification, documents, answers, and metadata

### 3. Data Processing Layer
- **Components**:
  - PDF Processor: Extracts text from factsheets
  - Document Chunker: Creates overlapping chunks (1000 chars, 200 overlap)
  - Embedding Generator: BGE-M3 local embeddings (1024 dimensions)

### 4. Storage Layer
- **Technology**: MongoDB Atlas
- **Purpose**: Vector database with semantic search
- **Features**:
  - Vector similarity search
  - Metadata filtering (month, fund_name)
  - Efficient retrieval with top-k results

### 5. AI Models
- **Gemini 2.5 Flash**: Query classification and answer generation
- **BGE-M3**: Local multilingual embeddings

---

## Low-Level Design

### Agent Workflow (LangGraph)

```
START
  │
  ▼
┌─────────────────────┐
│ Clarification Node  │
│                     │
│ • Checks ambiguity  │
│ • Asks questions    │
└──────┬──────────────┘
       │
       ├─[Needs Clarification]─→ END (Return question)
       │
       └─[Clear Query]
              │
              ▼
┌─────────────────────┐
│  Classifier Node    │
│                     │
│ • Gemini 2.5 Flash  │
│ • Intra vs Inter    │
│ • Extract months    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Retrieval Node     │
│                     │
│ • Vector search     │
│ • Metadata filter   │
│ • Top-5 results     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Generation Node    │
│                     │
│ • Gemini 2.5 Flash  │
│ • Grounded answer   │
│ • Extract citations │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Validation Node    │
│                     │
│ • Check grounding   │
│ • Confidence level  │
│ • Format response   │
└──────┬──────────────┘
       │
       ▼
      END
```

### State Schema

```python
AgentState:
  - query: str                          # User input
  - query_type: "intra" | "inter"       # Classification result
  - months_mentioned: List[str]         # Extracted months
  - needs_clarification: bool           # Ambiguity flag
  - clarification_question: str         # Question to ask
  - retrieved_docs: List[Document]      # Search results
  - answer: str                         # Generated response
  - citations: List[str]                # Source references
  - is_grounded: bool                   # Validation flag
  - confidence: "high" | "medium" | "low"
  - error: str                          # Error messages
```

### Node Implementations

#### 1. Clarification Node
```
Input: query
Process:
  - Analyze query for ambiguity
  - Check if month is specified
  - Determine if clarification needed
Output: needs_clarification, clarification_question
```

#### 2. Classifier Node
```
Input: query
Process:
  - Call Gemini 2.5 Flash with classification prompt
  - Parse response for query type
  - Extract mentioned months
Output: query_type, months_mentioned
```

#### 3. Retrieval Node
```
Input: query, query_type, months_mentioned
Process:
  - Generate query embedding (BGE-M3)
  - Build metadata filter based on months
  - Execute vector search on MongoDB
  - Return top-5 similar documents
Output: retrieved_docs
```

#### 4. Generation Node
```
Input: query, retrieved_docs
Process:
  - Format context from documents
  - Call Gemini 2.5 Flash with generation prompt
  - Extract answer and citations
  - Ensure grounding in source material
Output: answer, citations
```

#### 5. Validation Node
```
Input: answer, citations, retrieved_docs
Process:
  - Verify citations exist in documents
  - Check answer grounding
  - Determine confidence level
  - Format final response
Output: is_grounded, confidence
```

### Data Flow

#### Document Processing Pipeline
```
PDF Files
  │
  ▼
[PDFPlumber Extract]
  │
  ▼
Raw Text
  │
  ▼
[Chunk with Overlap]
  │ (1000 chars, 200 overlap)
  ▼
Text Chunks + Metadata
  │ {text, month, fund_name, page}
  ▼
[BGE-M3 Embedding]
  │ (1024 dimensions)
  ▼
Vector + Metadata
  │
  ▼
[MongoDB Atlas Insert]
  │
  ▼
Vector Database
```

#### Query Processing Pipeline
```
User Query
  │
  ▼
[Clarification Check]
  │
  ├─[Ambiguous]─→ Return Question
  │
  └─[Clear]
      │
      ▼
[Classify: Intra/Inter]
  │
  ▼
[Extract Months]
  │
  ▼
[Generate Embedding]
  │
  ▼
[Vector Search + Filter]
  │
  ▼
Top-K Documents
  │
  ▼
[Generate Answer]
  │
  ▼
[Validate & Cite]
  │
  ▼
Final Response
```

### MongoDB Schema

```javascript
{
  _id: ObjectId,
  text: String,              // Chunk content
  embedding: Array[1024],    // BGE-M3 vector
  month: String,             // "October", "November", "December"
  fund_name: String,         // Fund identifier
  page: Number,              // Source page number
  source: String             // PDF filename
}
```

### Vector Search Index Configuration

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

## Key Design Decisions

### 1. Local Embeddings (BGE-M3)
- **Why**: Cost-effective, no API calls, multilingual support
- **Trade-off**: Initial model download, local compute required
- **Benefit**: 1024 dimensions provide good semantic understanding

### 2. LangGraph for Orchestration
- **Why**: State management, conditional routing, visualization
- **Trade-off**: Learning curve for framework
- **Benefit**: Clear workflow, easy debugging, extensible

### 3. Metadata Filtering
- **Why**: Efficient retrieval, reduces irrelevant results
- **Trade-off**: Requires structured metadata
- **Benefit**: Fast queries, accurate month-specific answers

### 4. Gemini 2.5 Flash
- **Why**: Fast, cost-effective, good quality
- **Trade-off**: API dependency, rate limits
- **Benefit**: Reliable classification and generation

### 5. Strict Grounding
- **Why**: Prevent hallucinations, ensure accuracy
- **Trade-off**: May not answer all questions
- **Benefit**: Trustworthy responses with citations

## Performance Characteristics

- **Document Processing**: ~1500 chunks from 3 PDFs in <1 minute
- **Query Classification**: ~1-2 seconds (Gemini API)
- **Vector Search**: <500ms (MongoDB Atlas)
- **Answer Generation**: ~2-3 seconds (Gemini API)
- **Total Query Time**: ~4-6 seconds end-to-end

## Scalability Considerations

- **Horizontal**: Add more PDFs without code changes
- **Vertical**: MongoDB Atlas handles millions of vectors
- **Caching**: Can add Redis for frequent queries
- **Batch Processing**: Setup script handles bulk uploads

## Security & Privacy

- **API Keys**: Stored in .env, not committed
- **Data**: PDFs processed locally, vectors in MongoDB
- **Access**: MongoDB Atlas network restrictions
- **Validation**: Input sanitization in all nodes
