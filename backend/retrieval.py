import os
import chromadb
from sentence_transformers import SentenceTransformer
from backend.config import CHROMA_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL_NAME

# Global variables to cache Chroma client and BGE model
_chroma_client = None
_chroma_collection = None
_embedding_model = None

# Scheme keyword detection map
SCHEME_KEYWORDS = {
    "HDFC Mid-Cap Opportunities Fund": ["mid-cap", "mid cap", "midcap", "opportunities"],
    "HDFC Small Cap Fund": ["small-cap", "small cap", "smallcap"],
    "HDFC Gold ETF Fund of Fund": ["gold", "gold etf", "gold fof"],
    "HDFC Multi Cap Fund": ["multi-cap", "multi cap", "multicap"],
    "HDFC Top 100 Fund (Large Cap)": ["large-cap", "large cap", "top 100", "top100", "largecap"]
}

def get_chroma_collection():
    global _chroma_client, _chroma_collection
    if _chroma_collection is None:
        if not os.path.exists(CHROMA_DB_PATH):
            raise FileNotFoundError(f"Chroma database path '{CHROMA_DB_PATH}' not found. Run index.py first.")
        _chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        _chroma_collection = _chroma_client.get_collection(name=COLLECTION_NAME)
    return _chroma_collection

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model

def detect_scheme(query: str) -> str:
    """Scans the query for keywords matching one of the 5 target schemes."""
    query_lower = query.lower()
    for scheme_name, keywords in SCHEME_KEYWORDS.items():
        if any(keyword in query_lower for keyword in keywords):
            return scheme_name
    return ""

def rerank_and_boost_tables(query: str, chunks: list) -> list:
    """Prioritizes chunks containing Markdown tables if the query contains table-related keywords."""
    query_lower = query.lower()
    table_keywords = ["load", "ratio", "fee", "aum", "minimum", "sip", "table"]
    
    if not any(keyword in query_lower for keyword in table_keywords):
        return chunks
        
    table_chunks = []
    text_chunks = []
    
    for chunk in chunks:
        text = chunk["text"]
        # Check if the chunk contains a markdown table structure
        if "|" in text and "---" in text:
            table_chunks.append(chunk)
        else:
            text_chunks.append(chunk)
            
    # Return table chunks first, followed by text chunks to boost table context visibility for LLM
    return table_chunks + text_chunks

def retrieve_context(query: str, k: int = 6) -> list[dict]:
    """Retrieves top k chunks matching the query with scheme-specific metadata filtering and table boosting."""
    collection = get_chroma_collection()
    model = get_embedding_model()
    
    # 1. Detect target scheme
    target_scheme = detect_scheme(query)
    
    # 2. Formulate metadata filter to prevent cross-fund contamination
    metadata_filter = None
    if target_scheme:
        print(f"Detected target scheme: '{target_scheme}'. Applying metadata filters.")
        # Filter chunks that belong to the detected scheme OR general guides OR regulatory sources
        metadata_filter = {
            "$or": [
                {"scheme_name": target_scheme},
                {"scheme_name": "General HDFC MF"},
                {"scheme_name": "Regulatory AMFI"},
                {"scheme_name": "Regulatory SEBI"}
            ]
        }
    else:
        print("No specific scheme detected. Querying entire collection.")
        
    # 3. Compute query embedding
    query_vector = model.encode(query).tolist()
    
    # 4. Search Chroma DB
    search_results = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        where=metadata_filter,
        include=["documents", "metadatas", "distances"]
    )
    
    # 5. Format chunks
    chunks = []
    if search_results["ids"] and len(search_results["ids"][0]) > 0:
        for idx in range(len(search_results["ids"][0])):
            chunks.append({
                "id": search_results["ids"][0][idx],
                "text": search_results["documents"][0][idx],
                "metadata": search_results["metadatas"][0][idx],
                "distance": search_results["distances"][0][idx]
            })
            
    # 6. Apply tabular reranking
    reranked_chunks = rerank_and_boost_tables(query, chunks)
    
    return reranked_chunks
