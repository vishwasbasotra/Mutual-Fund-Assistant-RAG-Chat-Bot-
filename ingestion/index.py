import os
import json
import re

# Directory paths
PARSED_DIR = "parsed_data"
CHUNKS_FILE = os.path.join(PARSED_DIR, "chunks.json")

def parse_yaml_frontmatter(content):
    """Parses YAML frontmatter from the top of the file."""
    # Frontmatter is expected between the first two triple-dash lines '---'
    parts = content.split("---", 2)
    metadata = {}
    body = content
    
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = parts[2]
        # Parse simple key-value pairs from frontmatter
        for line in frontmatter.splitlines():
            line = line.strip()
            if line and ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip()] = val.strip()
                
    return metadata, body.strip()

def chunk_text_block(text, chunk_size=512, overlap=64):
    """Chunks a block of plain text semantically by paragraphs/sentences."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
            
        # If paragraph is too large, split it into sentences
        if len(p) > chunk_size:
            # Flush current chunk if any
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
                
            # Split paragraph into sentences using regex (split by period/exclamation/question mark followed by spaces)
            sentences = re.split(r'(?<=[.!?]) +', p)
            temp_chunk = ""
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                # If sentence itself is longer than chunk_size, split by character
                if len(s) > chunk_size:
                    # Flush temp_chunk first
                    if temp_chunk:
                        chunks.append(temp_chunk)
                        temp_chunk = ""
                    # Split by characters
                    for i in range(0, len(s), chunk_size - overlap):
                        chunks.append(s[i:i + chunk_size])
                else:
                    if len(temp_chunk) + len(s) + 1 <= chunk_size:
                        temp_chunk += (" " if temp_chunk else "") + s
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk)
                        # Carry over overlap if possible
                        overlap_start = max(0, len(temp_chunk) - overlap)
                        overlap_text = temp_chunk[overlap_start:]
                        temp_chunk = (overlap_text + " " + s).strip()
            if temp_chunk:
                chunks.append(temp_chunk)
        else:
            # Paragraph fits inside chunk_size
            if len(current_chunk) + len(p) + 2 <= chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + p
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # Group next chunk with overlap from previous chunk
                overlap_start = max(0, len(current_chunk) - overlap)
                overlap_text = current_chunk[overlap_start:].strip()
                current_chunk = (overlap_text + "\n\n" + p).strip() if overlap_text else p
                
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def split_document_with_tables(text, chunk_size=512, overlap=64):
    """Splits a document, preserving entire Markdown tables as whole chunks."""
    lines = text.splitlines()
    blocks = []
    current_block = []
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        # Detect markdown table lines (starts and ends with |)
        is_table_line = stripped.startswith("|") and stripped.endswith("|")
        
        if is_table_line:
            if not in_table:
                # Flush existing text block
                if current_block:
                    blocks.append({"type": "text", "content": "\n".join(current_block)})
                    current_block = []
                in_table = True
            current_block.append(line)
        else:
            if in_table:
                # Flush existing table block
                if current_block:
                    blocks.append({"type": "table", "content": "\n".join(current_block)})
                    current_block = []
                in_table = False
            current_block.append(line)
            
    # Flush final block
    if current_block:
        blocks.append({"type": "table" if in_table else "text", "content": "\n".join(current_block)})
        
    chunks = []
    for block in blocks:
        if block["type"] == "table":
            # Add table whole to preserve structural alignment for LLM
            chunks.append(block["content"])
        else:
            chunks.extend(chunk_text_block(block["content"], chunk_size, overlap))
            
    return chunks

def main():
    print("Starting semantic chunking & annotation...")
    
    if not os.path.exists(PARSED_DIR):
        print(f"Error: parsed directory '{PARSED_DIR}' not found. Run parser.py first.")
        return
        
    all_chunks = []
    parsed_files = [f for f in os.listdir(PARSED_DIR) if f.endswith(".txt") and f != "chunks.json"]
    
    for filename in parsed_files:
        file_path = os.path.join(PARSED_DIR, filename)
        print(f"Chunking: {filename}...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        metadata, body = parse_yaml_frontmatter(content)
        
        # Split document text keeping tables intact
        document_chunks = split_document_with_tables(body, chunk_size=512, overlap=64)
        
        for i, chunk_text in enumerate(document_chunks):
            # Annotate chunk with metadata and position index
            chunk_data = {
                "chunk_id": f"{filename[:-4]}_{i}",
                "text": chunk_text,
                "metadata": {
                    "source_url": metadata.get("source_url", ""),
                    "scheme_name": metadata.get("scheme_name", "General"),
                    "document_type": metadata.get("document_type", "FAQ"),
                    "last_updated": metadata.get("last_updated", "June 5, 2026"),
                    "chunk_index": i
                }
            }
            all_chunks.append(chunk_data)
            
    # Write all chunks to chunks.json
    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
        
    print(f"Completed! Created {len(all_chunks)} semantic chunks. Saved to: {CHUNKS_FILE}")

    # --- Phase 1.4: Vector Store Ingestion ---
    print("\nStarting Vector Store Ingestion into Chroma DB...")
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        
        # Initialize Persistent Chroma Client
        db_path = "chroma_db"
        print(f"Initializing Chroma DB client at '{db_path}'...")
        client = chromadb.PersistentClient(path=db_path)
        
        # Get or create collection
        collection_name = "mutual_fund_faq"
        print(f"Creating/getting Chroma collection: '{collection_name}'...")
        collection = client.get_or_create_collection(name=collection_name)
        
        # Load local BGE model (will download and cache on first run)
        model_name = "BAAI/bge-small-en-v1.5"
        print(f"Loading embedding model: '{model_name}'...")
        model = SentenceTransformer(model_name)
        
        # Batch insert chunks
        ids = [chunk["chunk_id"] for chunk in all_chunks]
        texts = [chunk["text"] for chunk in all_chunks]
        metadatas = [chunk["metadata"] for chunk in all_chunks]
        
        print("Computing BGE embeddings for chunks...")
        embeddings = model.encode(texts, show_progress_bar=True).tolist()
        
        print(f"Adding {len(all_chunks)} documents to Chroma DB...")
        
        # Delete existing entries in collection first to prevent duplication on runs
        existing_ids = collection.get()["ids"]
        if existing_ids:
            print(f"Clearing {len(existing_ids)} existing entries in collection...")
            collection.delete(ids=existing_ids)
            
        # Add to collection
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        print("Successfully ingested all chunks into local Chroma database!")
        
    except Exception as e:
        print(f"Error during Vector Store Ingestion: {e}")

if __name__ == "__main__":
    main()
