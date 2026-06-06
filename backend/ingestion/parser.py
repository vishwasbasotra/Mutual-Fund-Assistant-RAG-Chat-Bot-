import os
import json
import re
import shutil
from bs4 import BeautifulSoup

# Ensure parsed_data directory exists
os.makedirs("parsed_data", exist_ok=True)

# Try importing pdfplumber
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

# Mapping of file base names to standard metadata details
METADATA_MAP = {
    "hdfc_midcap_groww": {
        "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "scheme_name": "HDFC Mid-Cap Opportunities Fund",
        "document_type": "Groww Scheme Page",
        "last_updated": "May 31, 2026"
    },
    "hdfc_smallcap_groww": {
        "source_url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        "scheme_name": "HDFC Small Cap Fund",
        "document_type": "Groww Scheme Page",
        "last_updated": "May 31, 2026"
    },
    "hdfc_gold_groww": {
        "source_url": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
        "scheme_name": "HDFC Gold ETF Fund of Fund",
        "document_type": "Groww Scheme Page",
        "last_updated": "May 31, 2026"
    },
    "hdfc_multicap_groww": {
        "source_url": "https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth",
        "scheme_name": "HDFC Multi Cap Fund",
        "document_type": "Groww Scheme Page",
        "last_updated": "May 31, 2026"
    },
    "hdfc_largecap_groww": {
        "source_url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
        "scheme_name": "HDFC Top 100 Fund (Large Cap)",
        "document_type": "Groww Scheme Page",
        "last_updated": "May 31, 2026"
    },
    "hdfc_midcap_sid": {
        "source_url": "https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Mid-Cap_Opportunities_Fund_June_2024.pdf",
        "scheme_name": "HDFC Mid-Cap Opportunities Fund",
        "document_type": "Scheme Information Document",
        "last_updated": "June 30, 2024"
    },
    "hdfc_smallcap_sid": {
        "source_url": "https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Small_Cap_Fund_June_2024.pdf",
        "scheme_name": "HDFC Small Cap Fund",
        "document_type": "Scheme Information Document",
        "last_updated": "June 30, 2024"
    },
    "hdfc_gold_sid": {
        "source_url": "https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Gold_ETF_FOF_June_2024.pdf",
        "scheme_name": "HDFC Gold ETF Fund of Fund",
        "document_type": "Scheme Information Document",
        "last_updated": "June 30, 2024"
    },
    "hdfc_multicap_sid": {
        "source_url": "https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Multi_Cap_Fund_June_2024.pdf",
        "scheme_name": "HDFC Multi Cap Fund",
        "document_type": "Scheme Information Document",
        "last_updated": "June 30, 2024"
    },
    "hdfc_largecap_sid": {
        "source_url": "https://www.hdfcfund.com/sites/default/files/2024-06/SID_HDFC_Large_Cap_Fund_June_2024.pdf",
        "scheme_name": "HDFC Top 100 Fund (Large Cap)",
        "document_type": "Scheme Information Document",
        "last_updated": "June 30, 2024"
    },
    "hdfc_midcap_factsheet": {
        "source_url": "https://www.hdfcfund.com/sites/default/files/factsheets/HDFC_Mid-Cap_Opportunities_Factsheet.pdf",
        "scheme_name": "HDFC Mid-Cap Opportunities Fund",
        "document_type": "Factsheet",
        "last_updated": "May 31, 2026"
    },
    "hdfc_smallcap_factsheet": {
        "source_url": "https://www.hdfcfund.com/sites/default/files/factsheets/HDFC_Small_Cap_Factsheet.pdf",
        "scheme_name": "HDFC Small Cap Fund",
        "document_type": "Factsheet",
        "last_updated": "May 31, 2026"
    },
    "hdfc_gold_factsheet": {
        "source_url": "https://www.hdfcfund.com/sites/default/files/factsheets/HDFC_Gold_ETF_FOF_Factsheet.pdf",
        "scheme_name": "HDFC Gold ETF Fund of Fund",
        "document_type": "Factsheet",
        "last_updated": "May 31, 2026"
    },
    "hdfc_multicap_factsheet": {
        "source_url": "https://www.hdfcfund.com/sites/default/files/factsheets/HDFC_Multi_Cap_Factsheet.pdf",
        "scheme_name": "HDFC Multi Cap Fund",
        "document_type": "Factsheet",
        "last_updated": "May 31, 2026"
    },
    "hdfc_largecap_factsheet": {
        "source_url": "https://www.hdfcfund.com/sites/default/files/factsheets/HDFC_Large_Cap_Factsheet.pdf",
        "scheme_name": "HDFC Top 100 Fund (Large Cap)",
        "document_type": "Factsheet",
        "last_updated": "May 31, 2026"
    },
    "hdfc_statement_request": {
        "source_url": "https://www.hdfcfund.com/investor-services/statement-request",
        "scheme_name": "General HDFC MF",
        "document_type": "Guide",
        "last_updated": "June 5, 2026"
    },
    "hdfc_cas_download": {
        "source_url": "https://www.hdfcfund.com/investor-services/consolidated-account-statement",
        "scheme_name": "General HDFC MF",
        "document_type": "Guide",
        "last_updated": "June 5, 2026"
    },
    "hdfc_faqs": {
        "source_url": "https://www.hdfcfund.com/information/faqs",
        "scheme_name": "General HDFC MF",
        "document_type": "FAQ",
        "last_updated": "June 5, 2026"
    },
    "amfi_faq": {
        "source_url": "https://www.amfiindia.com/investor-corner/faq",
        "scheme_name": "Regulatory AMFI",
        "document_type": "FAQ",
        "last_updated": "June 5, 2026"
    },
    "sebi_faq": {
        "source_url": "https://www.sebi.gov.in/sebiweb/home/list/4/37/0/1/FAQs",
        "scheme_name": "Regulatory SEBI",
        "document_type": "FAQ",
        "last_updated": "June 5, 2026"
    }
}

def html_table_to_markdown(table):
    """Converts a BeautifulSoup <table> into a Markdown table."""
    rows = table.find_all("tr")
    if not rows:
        return ""
        
    markdown_lines = []
    max_cells = 0
    
    # Track row index to detect headers
    for i, row in enumerate(rows):
        cells = row.find_all(["th", "td"])
        cell_texts = [cell.get_text(strip=True).replace("\n", " ").replace("|", "\\|") for cell in cells]
        
        if not cell_texts:
            continue
            
        max_cells = max(max_cells, len(cell_texts))
        line = "| " + " | ".join(cell_texts) + " |"
        markdown_lines.append(line)
        
        # Insert divider after the header (row 0)
        if i == 0:
            markdown_lines.append("divider_placeholder")
            
    # Fix separator line with appropriate column count
    for idx, line in enumerate(markdown_lines):
        if line == "divider_placeholder":
            markdown_lines[idx] = "| " + " | ".join(["---"] * max_cells) + " |"
            
    return "\n\n" + "\n".join(markdown_lines) + "\n\n"

def parse_html_file(file_path):
    """Cleans up raw HTML files and extracts clean text and tables."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove script, style, nav, footer, header elements
    for el in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe"]):
        el.decompose()
        
    # Convert all HTML tables to Markdown tables
    for table in soup.find_all("table"):
        md_table = html_table_to_markdown(table)
        table.replace_with(md_table)
        
    # Insert double newlines around block level elements to preserve paragraphs and avoid merging metrics
    block_tags = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'ul', 'ol', 'section', 'article', 'br']
    for tag_name in block_tags:
        for tag in soup.find_all(tag_name):
            tag.insert_before('\n\n')
            tag.insert_after('\n\n')
            
    # Extract clean text
    text_content = soup.get_text(separator=" ")
    
    # Clean up duplicate spaces and group paragraphs
    text_content = re.sub(r'[ \t]+', ' ', text_content)
    text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
    
    # Strip unnecessary whitespaces and group lines
    lines = []
    for line in text_content.splitlines():
        line = line.strip()
        if line:
            # Skip noise lines commonly found in Groww headers or CSS listings
            if any(term in line.lower() for term in ["@media", "webkit-font", "font-family", "display:", "box-sizing:"]):
                continue
            lines.append(line)
            
    raw_text = "\n\n".join(lines)
    
    # If it is a Groww scheme page, apply template-specific noise filtering
    if "groww" in file_path.lower():
        lines_all = raw_text.split("\n\n")
        if lines_all:
            title_line = lines_all[0]
            cleaned_lines = [title_line]
            started = False
            
            for l in lines_all[1:]:
                l_strip = l.strip()
                if not started:
                    # Detect start of actual content (e.g. 3Y annualised returns or NAV metrics)
                    if "annualised" in l_strip.lower() or "nav:" in l_strip.lower() or "min. for sip" in l_strip.lower():
                        started = True
                
                if started:
                    # Detect start of site-wide footer links
                    if l_strip == "Home" or l_strip == "Vaishnavi Tech Park" or l_strip == "Contact Us" or l_strip.startswith("Sarjapur Main Road"):
                        break
                    cleaned_lines.append(l)
            
            if len(cleaned_lines) > 2:
                return "\n\n".join(cleaned_lines)
                
    return raw_text

def parse_pdf_file(file_path):
    """Uses pdfplumber to extract text and format tables from a PDF."""
    if not HAS_PDFPLUMBER:
        raise ImportError("pdfplumber is required for PDF parsing.")
        
    extracted_text = []
    with pdfplumber.open(file_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            
            # Check for tables
            tables = page.find_tables()
            if tables:
                # To avoid duplicating table text, we'll try to find where tables are on the page
                # For simplicity, extract table contents and format them
                for table in tables:
                    table_data = table.extract()
                    if not table_data:
                        continue
                    # Convert list of rows to markdown
                    md_lines = []
                    max_cols = 0
                    for row_idx, row in enumerate(table_data):
                        # Filter out None and replace newlines
                        row_cells = [str(cell or "").strip().replace("\n", " ").replace("|", "\\|") for cell in row]
                        max_cols = max(max_cols, len(row_cells))
                        md_lines.append("| " + " | ".join(row_cells) + " |")
                        if row_idx == 0:
                            md_lines.append("divider_placeholder")
                            
                    # Construct table markdown
                    for d_idx, d_line in enumerate(md_lines):
                        if d_line == "divider_placeholder":
                            md_lines[d_idx] = "| " + " | ".join(["---"] * max_cols) + " |"
                            
                    page_text += "\n\n" + "\n".join(md_lines) + "\n\n"
                    
            extracted_text.append(f"--- Page {idx+1} ---\n{page_text}")
            
    return "\n\n".join(extracted_text)

def generate_yaml_header(metadata):
    """Constructs a YAML frontmatter string from a metadata dict."""
    return f"""---
source_url: {metadata.get('source_url', '')}
scheme_name: {metadata.get('scheme_name', 'General')}
document_type: {metadata.get('document_type', 'FAQ')}
last_updated: {metadata.get('last_updated', 'June 5, 2026')}
---
"""

def main():
    print("Starting document parsing...")
    raw_files = os.listdir("raw_data")
    
    for filename in raw_files:
        raw_path = os.path.join("raw_data", filename)
        
        # Check base name for metadata matching
        base_name = filename
        if filename.endswith(".pdf.txt"):
            base_name = filename[:-8]
        elif "." in filename:
            base_name = filename.rsplit(".", 1)[0]
            
        metadata = METADATA_MAP.get(base_name, {
            "source_url": "https://www.hdfcfund.com",
            "scheme_name": "General",
            "document_type": "Document",
            "last_updated": "June 5, 2026"
        })
        
        out_filename = base_name + ".txt"
        out_path = os.path.join("parsed_data", out_filename)
        
        print(f"Parsing: {filename} -> {out_filename}")
        
        try:
            # Handle PDF.txt fallbacks
            if filename.endswith(".pdf.txt"):
                with open(raw_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # Remove mock header if present, since we append YAML header
                if "HDFC Mutual Fund" in content and "Source URL" in content:
                    # Content is already clean text fallback
                    pass
                parsed_text = content
                
            # Handle actual PDF files
            elif filename.endswith(".pdf"):
                if HAS_PDFPLUMBER:
                    parsed_text = parse_pdf_file(raw_path)
                else:
                    print(f"Warning: pdfplumber not installed, skipping binary PDF {filename}")
                    continue
                    
            # Handle HTML files
            elif filename.endswith(".html"):
                parsed_text = parse_html_file(raw_path)
                
            else:
                # Skip unknown types
                print(f"Skipping unknown file type: {filename}")
                continue
                
            # Write out text with YAML header
            yaml_header = generate_yaml_header(metadata)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(yaml_header)
                f.write("\n")
                f.write(parsed_text)
                
            print(f"Successfully processed and saved to {out_path}")
            
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            
    print("All file parsing finished. Parsed text stored in 'parsed_data/'.")

if __name__ == "__main__":
    main()
