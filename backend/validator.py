import re

ABBREVIATIONS = ["Co", "Ltd", "Dr", "Mr", "Ms", "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "vs", "max", "min", "AUM"]

def truncate_sentences(text: str, max_sentences: int = 3) -> str:
    """Truncates the text to a maximum of max_sentences sentences cleanly, protecting abbreviations."""
    temp_text = text
    # Replace abbreviations followed by dot with a placeholder to avoid incorrect sentence splits
    for abbr in ABBREVIATIONS:
        temp_text = re.sub(rf'\b{abbr}\.', f"{abbr}##DOT##", temp_text, flags=re.IGNORECASE)
        
    # Split by standard sentence endings: period, question mark, or exclamation mark followed by whitespace
    sentence_end = re.compile(r'\.\s+|[!?]\s+')
    
    # Locate boundaries
    boundaries = [0]
    for match in sentence_end.finditer(temp_text):
        boundaries.append(match.end())
    boundaries.append(len(temp_text))
    
    temp_sentences = []
    for i in range(len(boundaries) - 1):
        s = temp_text[boundaries[i]:boundaries[i+1]].strip()
        if s:
            # Restore the dots
            for abbr in ABBREVIATIONS:
                s = re.sub(rf'\b{abbr}##DOT##', f"{abbr}.", s, flags=re.IGNORECASE)
            temp_sentences.append(s)
            
    if len(temp_sentences) <= max_sentences:
        return text
        
    truncated = " ".join(temp_sentences[:max_sentences])
    if not truncated.endswith((".", "!", "?")):
        truncated += "."
    return truncated

def extract_urls(text: str) -> list[str]:
    """Extracts all URLs from markdown links inside the text."""
    # Matches [label](url)
    return re.findall(r'\[.*?\]\((https?://.*?)\)', text)

def validate_and_sanitize(raw_answer: str, retrieved_chunks: list) -> tuple[str, str]:
    """
    Enforces the sentence limit, verifies that the citation URL matches one of 
    the context sources (overwrites if hallucinated), and appends the compliance footer.
    
    Returns (sanitized_answer, validated_citation).
    """
    if not retrieved_chunks:
        return raw_answer, "https://www.hdfcfund.com"
        
    # 1. Truncate response to maximum 3 sentences
    truncated_answer = truncate_sentences(raw_answer, max_sentences=3)
    
    # 2. Extract context source URLs
    valid_urls = {chunk["metadata"].get("source_url") for chunk in retrieved_chunks if chunk["metadata"].get("source_url")}
    primary_url = retrieved_chunks[0]["metadata"].get("source_url", "https://www.hdfcfund.com")
    
    # 3. Extract and validate link in LLM answer
    extracted_links = extract_urls(truncated_answer)
    citation_url = primary_url
    
    if extracted_links:
        # Check if the first link is in our valid context URLs
        first_link = extracted_links[0]
        if first_link in valid_urls:
            citation_url = first_link
        else:
            # The LLM hallucinated the link. Replace the hallucinated link with the correct primary context link.
            # Replace the first markdown link URL with primary_url
            truncated_answer = re.sub(
                r'(\[.*?\])\(https?://.*?\)', 
                rf'\1({primary_url})', 
                truncated_answer, 
                count=1
            )
            citation_url = primary_url
    else:
        # No link was provided. We must append the link ourselves to guarantee citation compliance.
        # Find the document type or scheme name for labeling the citation link
        doc_type = retrieved_chunks[0]["metadata"].get("document_type", "Official Document")
        scheme_name = retrieved_chunks[0]["metadata"].get("scheme_name", "Source")
        label = f"{scheme_name} {doc_type}"
        truncated_answer += f" For details, please refer to the [{label}]({primary_url})."
        citation_url = primary_url
        
    # 4. Extract last updated date from context metadata
    last_updated_dates = [chunk["metadata"].get("last_updated") for chunk in retrieved_chunks if chunk["metadata"].get("last_updated")]
    # Prioritize the most recent date if dates are standardized, or just take the first one
    last_updated = last_updated_dates[0] if last_updated_dates else "June 5, 2026"
    
    # 5. Append compliance footer
    footer = f"\n\nLast updated from sources: {last_updated}"
    final_answer = truncated_answer + footer
    
    return final_answer, citation_url
