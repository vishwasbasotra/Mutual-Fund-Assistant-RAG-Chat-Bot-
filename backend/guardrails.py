import re
import requests
from backend.config import GROQ_API_KEY, GROQ_MODEL, GROQ_API_URL

# Regex patterns for PII
AADHAAR_PATTERN = re.compile(r'\b[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\b')
PAN_PATTERN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+91|91)?[6-9][0-9]{9}\b')
FOLIO_PATTERN = re.compile(r'\b[0-9]{5,12}/[0-9]{2,3}\b|\b[0-9]{7,12}\b')

REFUSAL_MESSAGE = (
    "I cannot provide investment advice, returns calculations, or scheme recommendations. "
    "You can learn more about objective investing on the "
    "[AMFI Investor Education Portal](https://www.amfiindia.com/investor-corner/education-series)."
)

PII_REJECTION_MESSAGE = (
    "For security and privacy reasons, please do not share personally identifiable information (PII) "
    "such as PAN card, Aadhaar number, folio numbers, bank accounts, emails, or phone numbers in your queries."
)

def check_pii(query: str) -> tuple[bool, str]:
    """Checks the query for any potential PII. Returns (has_pii, warning_message)."""
    if PAN_PATTERN.search(query):
        return True, PII_REJECTION_MESSAGE
    if AADHAAR_PATTERN.search(query):
        return True, PII_REJECTION_MESSAGE
    if EMAIL_PATTERN.search(query):
        return True, PII_REJECTION_MESSAGE
    if PHONE_PATTERN.search(query):
        return True, PII_REJECTION_MESSAGE
    if FOLIO_PATTERN.search(query):
        return True, PII_REJECTION_MESSAGE
        
    return False, ""

def check_advisory_intent(query: str) -> tuple[bool, str]:
    """Uses a fast classification prompt to check if the query is seeking advice or returns calculations."""
    query_lower = query.lower()
    
    # Bypass advisory checks for factual risk classifications / riskometers
    if any(r in query_lower for r in ["riskometer", "risk level", "risk profile", "risk classification"]):
        return False, ""
    advisory_keywords = [
        "should i buy", "should buy", "which is better", "best fund", "recommend", 
        "how much return", "interest rate", "calculate return", "how much will i get", 
        "compare", "growth prediction", "should i invest", "should invest", 
        "returns will i get", "how much returns", "predict", "investment advice", 
        "why i should", "why should i", "should i", "suggest", "advisory", "rating"
    ]
    
    matched_advisory = False
    for keyword in advisory_keywords:
        if keyword in query_lower:
            # Bypasses "rating" matches if they ask about "riskometer rating" or "risk rating"
            if keyword == "rating" and ("riskometer" in query_lower or "risk" in query_lower):
                continue
            matched_advisory = True
            break

    if matched_advisory:
        return True, REFUSAL_MESSAGE
        
    if not GROQ_API_KEY:
        print("Warning: GROQ_API_KEY is not set. Advisory check bypassed.")
        return False, ""
        
    # Call Groq for semantic classification
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = (
            "You are a strict financial compliance classifier.\n"
            "Your task is to classify if a user's query is seeking investment recommendations, opinions, advice, "
            "market predictions, returns/interest calculations, or performance ratings/comparisons of mutual funds.\n"
            "Respond with exactly one word: 'YES' if it is advisory/speculative/returns-seeking, or 'NO' if it is purely factual.\n"
            "Examples:\n"
            "Query: 'What is the exit load of HDFC Mid-cap?' -> NO\n"
            "Query: 'Is it safe to invest in small cap?' -> YES\n"
            "Query: 'How much returns will HDFC small cap give in 5 years?' -> YES\n"
            "Query: 'What is the risk level of HDFC Top 100 Fund?' -> NO\n"
            "Query: 'What is the riskometer rating of HDFC Small Cap?' -> NO\n"
            "Query: 'Who is the manager of HDFC Gold FoF?' -> NO"
        )
        
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: '{query}'"}
            ],
            "temperature": 0.0,
            "max_tokens": 5
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip().upper()
            if "YES" in content:
                return True, REFUSAL_MESSAGE
        else:
            print(f"Groq API Error in Guardrail: HTTP {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception in advisory guardrail: {e}")
        
    return False, ""
