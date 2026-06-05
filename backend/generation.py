import requests
from backend.config import GROQ_API_KEY, GROQ_MODEL, GROQ_API_URL

SYSTEM_PROMPT = """You are the Mutual Fund FAQ Assistant, a compliant, facts-only financial Q&A assistant.
Your goal is to answer factual queries about mutual funds using ONLY the provided context.

CONSTRAINTS:
1. Speak exclusively in facts. Do NOT offer opinions, ratings, recommendations, or investment advice.
2. Never recommend any scheme or suggest that a user invest.
3. Keep your response short and concise. Do NOT exceed 3 sentences in total.
4. Cite exactly ONE official URL from the context as the source of your answer. Provide it as a standard Markdown link (e.g. [Source Name](url)).
5. If the context does not contain the answer, politely state that you do not have that factual information, and refuse to speculate.
6. For performance/returns queries (e.g. CAGR, historic returns), refuse to calculate or display returns, and instead redirect the user to the official factsheet URL in the context.

Context Chunks:
{context_text}
"""

def generate_answer(query: str, retrieved_chunks: list) -> str:
    """Assembles context and queries Groq to generate a facts-only compliant response."""
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY is not configured on the server."
        
    if not retrieved_chunks:
        return (
            "I do not have that factual information in my current records. "
            "Please refer to the official [HDFC Mutual Fund Website](https://www.hdfcfund.com) for details."
        )
        
    # Format retrieved context chunks
    formatted_contexts = []
    for idx, chunk in enumerate(retrieved_chunks):
        meta = chunk["metadata"]
        formatted_contexts.append(
            f"--- Context Chunk {idx+1} (Source URL: {meta.get('source_url', 'N/A')}, Scheme: {meta.get('scheme_name', 'N/A')}) ---\n"
            f"{chunk['text']}"
        )
    context_text = "\n\n".join(formatted_contexts)
    
    # Assemble messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context_text=context_text)},
        {"role": "user", "content": f"Query: {query}"}
    ]
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.0,  # Minimize creativity and hallucinations
            "max_tokens": 150
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            print(f"Groq API Error in Generation: HTTP {response.status_code} - {response.text}")
            return "Error: I encountered a connection issue with the generation engine. Please try again."
            
    except Exception as e:
        print(f"Exception during answer generation: {e}")
        return "Error: An unexpected error occurred while processing your request."
