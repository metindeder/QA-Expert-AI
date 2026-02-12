import os
import shutil
from src.graph.code_parser import CodeGraphParser
from src.rag.vector_store import CodeVectorStore
from src.agent.llm_client import LLMClient

def main():
    # ---------------------------------------------------------
    # 1. GİRDİ: Ödeme Sistemi (Payment Module)
    # ---------------------------------------------------------
    print("\n--- STEP 1: Loading Input Data ---")
    
    dummy_code = """
    def process_payment(amount, currency, user_status):
        # Business Rule 1: Min amount is 10
        if amount < 10:
            return {"error": "Min amount 10"}
            
        # Business Rule 2: VIP users get 5% discount
        if user_status == "VIP":
            amount = amount * 0.95
            
        # Dependency: Bank API
        if connect_bank_api(amount, currency):
            return {"status": "Success", "charged": amount}
            
        return {"error": "Bank timeout"}
    """
    
    test_file = "data/raw_code/payment_module.py"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, "w") as f:
        f.write(dummy_code)

    # ---------------------------------------------------------
    # 2. PARSER & GRAPH
    # ---------------------------------------------------------
    print("\n--- STEP 2: Structural Analysis ---")
    parser = CodeGraphParser()
    parser.parse_file(test_file)

    # ---------------------------------------------------------
    # 3. VECTOR STORE
    # ---------------------------------------------------------
    print("\n--- STEP 3: Context Retrieval Setup ---")
    if os.path.exists("data/vector_db"):
        shutil.rmtree("data/vector_db")
    
    vector_store = CodeVectorStore()
    vector_store.add_graph_documents(parser.graph)

    # ---------------------------------------------------------
    # 4. AI GENERATION (Model: gherkin-qa)
    # ---------------------------------------------------------
    print("\n--- STEP 4: Generating QA Specifications ---")
    
    query = "Analyze this payment logic and create a Gherkin Feature file."
    
    results = vector_store.search_similar(query, k=1)
    
    if results['documents']:
        code_context = results['documents'][0][0]
        metadata = results['metadatas'][0][0]
        
        # GÜNCELLEME: Model ismini 'gherkin-qa' yaptık
        llm = LLMClient(model_name="gherkin-qa") 
        
        print(f"\n[AI AGENT 'gherkin-qa' WORKING]...")
        response = llm.generate_response(code_context, metadata, query)
        
        print("\n" + "="*40)
        print("GENERATED GHERKIN FEATURE FILE")
        print("="*40)
        print(response)
        print("="*40)
        
        with open("tests/payment.feature", "w", encoding="utf-8") as f:
            f.write(response)
        print("\n✅ Feature file saved to 'tests/payment.feature'")
        
    else:
        print("Error: Context not found.")

if __name__ == "__main__":
    main()