# Migration from Gemini Embeddings to BGE-M3

## Summary of Changes

Successfully migrated from Google Gemini embeddings to BGE-M3 (BAAI) local embedding model to eliminate API rate limiting issues.

## What Changed

### 1. Embedding Model
- **Before**: `gemini-embedding-001` (3072 dimensions, API-based, rate limited)
- **After**: `BAAI/bge-m3` (1024 dimensions, local, no rate limits)

### 2. Files Modified

#### `config.py`
- Changed `EMBEDDING_MODEL` from `"gemini-embedding-001"` to `"BAAI/bge-m3"`

#### `utils/embeddings.py`
- Replaced `GoogleGenerativeAIEmbeddings` with `HuggingFaceEmbeddings`
- Removed retry logic (no longer needed - no API calls)
- Added BGE-M3 specific configuration
- Model runs locally on CPU (can use GPU if available)

#### `utils/mongodb_handler.py`
- Updated vector index dimensions from 3072 to 1024

#### `setup_database.py`
- Updated vector index configuration from 3072 to 1024 dimensions

#### `requirements.txt`
- Added: `langchain-huggingface`, `sentence-transformers`
- Kept: All existing dependencies (Gemini still used for generation/classification)

## BGE-M3 Model Specifications

- **Dimensions**: 1024
- **Max Input Length**: 8192 tokens
- **Languages**: 100+ languages supported
- **Runs**: Locally (no API calls, no rate limits)
- **Performance**: State-of-the-art on MTEB Multilingual leaderboard
- **Features**: Dense retrieval, sparse retrieval, multi-vector (ColBERT)

## IMPORTANT: MongoDB Atlas Index Update Required

⚠️ **You MUST update your MongoDB Atlas vector search index before running the setup!**

### Steps to Update Index:

1. Go to MongoDB Atlas Dashboard
2. Navigate to your cluster → Database → Search
3. Find the index named `vector_index_1`
4. **Delete the old index** (or edit if possible)
5. **Create a new index** with this configuration:

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

**Key Change**: `numDimensions` changed from **3072** to **1024**

## Next Steps

1. ✅ Dependencies installed (already done with UV)
2. ⚠️ **Update MongoDB Atlas vector index** (see above)
3. ✅ Clear existing embeddings: `python setup_database.py` (it will clear old data)
4. ✅ Run setup: The script will now use BGE-M3 locally

## Running the Setup

```bash
cd Finance_Agent
python setup_database.py
```

### What to Expect:
- First run will download the BGE-M3 model (~1-2GB) from HuggingFace
- Model will be cached locally for future use
- No API rate limits - processes all documents without delays
- Slightly slower than API calls but much more reliable

## Benefits of BGE-M3

✅ **No Rate Limits**: Runs locally, process unlimited documents
✅ **No API Costs**: Completely free after initial download
✅ **Privacy**: Data never leaves your machine
✅ **Multilingual**: Better support for non-English text
✅ **Reliable**: No network dependency after initial download
✅ **Performance**: State-of-the-art quality on benchmarks

## Troubleshooting

### If you get dimension mismatch errors:
- Make sure you updated the MongoDB Atlas index to 1024 dimensions
- Clear old embeddings: The setup script does this automatically

### If model download is slow:
- First run downloads ~1-2GB model from HuggingFace
- Subsequent runs use cached model (fast)

### If you want to use GPU:
- Edit `utils/embeddings.py`
- Change `model_kwargs = {'device': 'cpu'}` to `model_kwargs = {'device': 'cuda'}`
- Requires CUDA-compatible GPU and drivers

## Reverting to Gemini (if needed)

If you need to revert:
1. Change `EMBEDDING_MODEL` in `config.py` back to `"gemini-embedding-001"`
2. Update `utils/embeddings.py` to use `GoogleGenerativeAIEmbeddings`
3. Update MongoDB index back to 3072 dimensions
4. Re-run setup

## Questions?

- BGE-M3 Documentation: https://huggingface.co/BAAI/bge-m3
- LangChain HuggingFace: https://python.langchain.com/docs/integrations/text_embedding/huggingfacehub
