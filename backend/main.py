import sys
import os

# Metaprogramming fallback to mock the 'backend' package when running on Railway
# where the root directory is set to 'backend' (mapping files directly to /app)
if 'backend' not in sys.modules:
    try:
        import backend
    except ModuleNotFoundError:
        import types
        backend_module = types.ModuleType('backend')
        sys.modules['backend'] = backend_module
        
        # Resolve sibling modules relative to current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        import config
        import guardrails
        import retrieval
        import generation
        import validator
        
        backend_module.config = config
        backend_module.guardrails = guardrails
        backend_module.retrieval = retrieval
        backend_module.generation = generation
        backend_module.validator = validator
        
        sys.modules['backend.config'] = config
        sys.modules['backend.guardrails'] = guardrails
        sys.modules['backend.retrieval'] = retrieval
        sys.modules['backend.generation'] = generation
        sys.modules['backend.validator'] = validator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.guardrails import check_pii, check_advisory_intent
from backend.retrieval import retrieve_context, detect_scheme
from backend.generation import generate_answer
from backend.validator import validate_and_sanitize
import uvicorn
import re

app = FastAPI(title="Facts-Only Mutual Fund FAQ Assistant API")

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    text: str

class QueryResponse(BaseModel):
    text: str
    citation: str
    refused: bool

# Scheme-specific keywords requiring a scheme target
SCHEME_SPECIFIC_KEYWORDS = [
    "exit load", "load", "expense ratio", "recurring expense", "ter", "fee", "charges", 
    "nav", "net asset value", "aum", "fund size", "assets", "sip", "minimum investment", 
    "lumpsum", "minimum", "holdings", "portfolio", "manager", "riskometer", "benchmark",
    "risk level", "risk"
]

def check_ambiguity(query: str) -> tuple[bool, str]:
    """Checks if the query contains scheme-specific keywords but does not specify a target scheme."""
    query_lower = query.lower()
    
    # Check if any scheme-specific keyword is present with word boundaries
    has_specific_keyword = False
    for kw in SCHEME_SPECIFIC_KEYWORDS:
        if re.search(rf'\b{re.escape(kw)}\b', query_lower):
            has_specific_keyword = True
            break
            
    if not has_specific_keyword:
        return False, ""
        
    # Check if a scheme is detected
    target_scheme = detect_scheme(query)
    if target_scheme:
        return False, ""
        
    # It has a scheme-specific keyword but no scheme was detected
    ambiguity_refusal = (
        "Could you please specify which HDFC Mutual Fund scheme you are referring to? "
        "I support the following schemes:\n"
        "- HDFC Mid-Cap Opportunities Fund\n"
        "- HDFC Small Cap Fund\n"
        "- HDFC Gold ETF Fund of Fund\n"
        "- HDFC Multi Cap Fund\n"
        "- HDFC Top 100 Fund (Large Cap)"
    )
    return True, ambiguity_refusal

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Mutual Fund FAQ Assistant Backend is live!"}

@app.get("/health")
def health_check():
    """Endpoint for checking DB connection and vector status."""
    try:
        from backend.retrieval import get_chroma_collection
        collection = get_chroma_collection()
        count = collection.count()
        return {
            "status": "healthy",
            "chroma_db": "connected",
            "document_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "chroma_db": "disconnected",
            "error": str(e)
        }

@app.post("/query", response_model=QueryResponse)
def query_assistant(request: QueryRequest):
    query = request.text.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")
        
    print(f"\nProcessing user query: '{query}'")
    
    # 1. Check for PII Leakage
    has_pii, pii_warning = check_pii(query)
    if has_pii:
        print("PII Detected. Blocking query.")
        return QueryResponse(
            text=pii_warning,
            citation="",
            refused=True
        )
        
    # 2. Check for Advisory / Return-Calculation Intent
    is_advisory, advisory_refusal = check_advisory_intent(query)
    if is_advisory:
        print("Advisory / Speculative query detected. Bypassing RAG and returning refusal.")
        return QueryResponse(
            text=advisory_refusal,
            citation="https://www.amfiindia.com/investor-corner/education-series",
            refused=True
        )
        
    # 2.5 Check for Query Ambiguity
    is_ambiguous, ambiguity_refusal = check_ambiguity(query)
    if is_ambiguous:
        print("Ambiguous query detected (scheme-specific keywords without target scheme). Returning clarification.")
        return QueryResponse(
            text=ambiguity_refusal,
            citation="",
            refused=True
        )
        
    # 3. Retrieve context chunks from Vector DB
    try:
        context_chunks = retrieve_context(query, k=6)
    except Exception as e:
        print(f"Retrieval Error: {e}")
        return QueryResponse(
            text="I encountered an error accessing my records. Please try again later.",
            citation="",
            refused=True
        )
        
    # 4. Generate raw completion from Groq LLM
    raw_answer = generate_answer(query, context_chunks)
    
    # 5. Sanitize and validate against strict compliance bounds
    sanitized_answer, citation_url = validate_and_sanitize(raw_answer, context_chunks)
    
    print(f"Compliance validation passed. Citation URL: '{citation_url}'")
    return QueryResponse(
        text=final_cleaning(sanitized_answer),
        citation=citation_url,
        refused=False
    )

def final_cleaning(text: str) -> str:
    """Performs minor text formatting cleanups to ensure output matches expected styles."""
    # Ensure double newlines preceding citation footer are formatted nicely
    text = text.replace("\n\nLast updated", "\n\nLast updated")
    # Replace raw emails inside text to protected version if any leaked through LLM
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[Protected Email]', text)
    return text

if __name__ == "__main__":
    from backend.config import HOST, PORT
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
