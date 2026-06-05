import os
import json

def run_tests():
    print("=" * 60)
    print("RUNNING PHASE 1 VERIFICATION TEST CASES")
    print("=" * 60)
    
    # --- Test Case 1.1: Noise Elimination ---
    print("\n--- Test Case 1.1: Noise Elimination ---")
    txt_path = "parsed_data/hdfc_gold_groww.txt"
    if not os.path.exists(txt_path):
        print(f"FAIL: {txt_path} not found.")
        tc1_pass = False
    else:
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for noise terms
        noise_terms = ["SBI Contra", "Quant Mid Cap", "Tata Ethical", "EPF Calculator"]
        found_terms = [term for term in noise_terms if term in content]
        
        if not found_terms:
            print(f"PASS: No competitor links or generic site noise found in {txt_path}.")
            tc1_pass = True
        else:
            print(f"FAIL: Found competitive noise elements in {txt_path}: {found_terms}")
            tc1_pass = False
            
    # --- Test Case 1.2: Markdown Tables ---
    print("\n--- Test Case 1.2: Markdown Tables ---")
    sid_path = "parsed_data/hdfc_midcap_sid.txt"
    if not os.path.exists(sid_path):
        print(f"FAIL: {sid_path} not found.")
        tc2_pass = False
    else:
        with open(sid_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        expected_table = "| Redemption Period | Exit Load |"
        expected_row = "| Within 1 Year (<= 365 Days) from allotment | 1.00% of applicable NAV |"
        
        if expected_table in content and expected_row in content:
            print(f"PASS: Exit load table correctly formatted in {sid_path}.")
            tc2_pass = True
        else:
            print(f"FAIL: Expected table markers not found in {sid_path}.")
            tc2_pass = False
            
    # --- Test Case 1.3: DB Fetch Check ---
    print("\n--- Test Case 1.3: DB Fetch Check ---")
    try:
        import chromadb
        client = chromadb.PersistentClient(path="chroma_db")
        collection = client.get_collection("mutual_fund_faq")
        count = collection.count()
        results = collection.get(limit=1, include=["embeddings", "metadatas"])
        
        if count > 0 and len(results["ids"]) > 0:
            embedding = results["embeddings"][0]
            dimension = len(embedding)
            if dimension == 384:
                print(f"PASS: Found {count} documents in Chroma collection. Embedding dimensions are verified to be {dimension}.")
                tc3_pass = True
            else:
                print(f"FAIL: Embedding dimension mismatch. Expected 384, found {dimension}.")
                tc3_pass = False
        else:
            print("FAIL: Chroma collection is empty.")
            tc3_pass = False
    except Exception as e:
        print(f"FAIL: Error during database validation: {e}")
        tc3_pass = False
        
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print(f"Test Case 1.1 (Noise Elimination): {'PASS' if tc1_pass else 'FAIL'}")
    print(f"Test Case 1.2 (Markdown Tables): {'PASS' if tc2_pass else 'FAIL'}")
    print(f"Test Case 1.3 (DB Fetch Check): {'PASS' if tc3_pass else 'FAIL'}")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
