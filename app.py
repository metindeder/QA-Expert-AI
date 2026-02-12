import streamlit as st
import os
import shutil
import time
import uuid
import zipfile

# Helper Modules
from src.graph.code_parser import CodeGraphParser
from src.rag.vector_store import CodeVectorStore
from src.agent.llm_client import LLMClient
from src.utils.pdf_processor import extract_text_from_pdf

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="QA Expert AI", layout="wide")

# --- SESSION STATE MANAGEMENT ---
# Ensures data persistence across Streamlit's rerun cycles
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'file_summary' not in st.session_state:
    st.session_state.file_summary = []
if 'node_count' not in st.session_state:
    st.session_state.node_count = 0
if 'edge_count' not in st.session_state:
    st.session_state.edge_count = 0
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("System Settings")
    
    # Dynamically fetch available models from Ollama
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models_json = response.json()
            available_models = [m['name'] for m in models_json['models']]
        else:
            available_models = ["gherkin-qa", "llama3"]
    except:
        available_models = ["gherkin-qa", "llama3"]

    model_name = st.selectbox("Select LLM Model", available_models, index=0)
    
    st.divider()
    st.markdown(f"**System Status:** :green[Active]")
    st.markdown(f"**Selected Model:** `{model_name}`")
    st.divider()
    
    if st.button("Reset Session"):
        st.session_state.session_id = f"session_{int(time.time())}"
        st.session_state.analysis_complete = False
        st.session_state.file_summary = []
        st.rerun()

# --- MAIN INTERFACE ---
st.title("QA Expert AI: Comprehensive Test Scenario Generator")
st.markdown("""
This agent analyzes your **Project Repositories** and **Requirement Documents** to build a structural 
Knowledge Graph and generate production-ready **Gherkin Test Scenarios**.
""")

tab1, tab2 = st.tabs(["📂 Upload Files/ZIP", "📍 Local Directory Path"])

files_to_process = []

# --- FILE FILTERING LOGIC ---
def is_valid_file(file_name):
    """
    Filters out non-relevant files like READMEs and media.
    Supports all text-based source code files and PDFs.
    """
    name_lower = file_name.lower()
    if name_lower == "readme.md":
        return False
    
    # Allowed: Source code, requirements, and text documentation
    valid_extensions = ('.py', '.pdf', '.txt', '.md', '.java', '.cpp', '.js', '.ts', '.c', '.cs', '.go')
    return name_lower.endswith(valid_extensions)

# --- INPUT METHOD 1: DRAG & DROP ---
with tab1:
    uploaded_files = st.file_uploader(
        "Drop source code files, requirement PDFs, or project ZIPs here. (READMEs and media are automatically filtered)",
        accept_multiple_files=True,
        type=['py', 'pdf', 'txt', 'zip', 'md', 'java', 'cpp', 'js', 'ts']
    )

# --- INPUT METHOD 2: LOCAL DIRECTORY ---
with tab2:
    local_path_input = st.text_input("Enter the full local path of your project (e.g., C:/Users/Dev/Project)", "")

# --- EXECUTION: ANALYSIS ---
if st.button("🚀 Start Project Analysis"):
    temp_dir = "data/temp_project"
    if os.path.exists(temp_dir):
        try: shutil.rmtree(temp_dir)
        except: pass
    os.makedirs(temp_dir, exist_ok=True)
    
    parser = CodeGraphParser()
    full_context_summary = []
    
    with st.status("Filtering and indexing files...", expanded=True) as status:
        st.write("Initializing Neuro-Symbolic Parser...")
        
        # Scenario A: Handle Uploaded Files
        if uploaded_files:
            for up_file in uploaded_files:
                if up_file.name.endswith(".zip"):
                    with zipfile.ZipFile(up_file, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if is_valid_file(file) and "__MACOSX" not in root:
                                files_to_process.append(os.path.join(root, file))
                else:
                    if is_valid_file(up_file.name):
                        file_path = os.path.join(temp_dir, up_file.name)
                        with open(file_path, "wb") as f:
                            f.write(up_file.getbuffer())
                        files_to_process.append(file_path)

        # Scenario B: Handle Local Path
        elif local_path_input and os.path.isdir(local_path_input):
            for root, dirs, files in os.walk(local_path_input):
                # Prune unnecessary directories
                for skip in ['venv', '.git', '__pycache__', 'node_modules', '.idea', 'dist', 'build']:
                    if skip in dirs: dirs.remove(skip)
                
                for file in files:
                    if is_valid_file(file):
                        src_path = os.path.join(root, file)
                        dst_path = os.path.join(temp_dir, file)
                        shutil.copy2(src_path, dst_path)
                        files_to_process.append(dst_path)

        # Process found files
        total_files = len(files_to_process)
        if total_files == 0:
            st.error("No valid source or requirement files found!")
            st.stop()
            
        for i, file_path in enumerate(files_to_process):
            file_name = os.path.basename(file_path)
            
            # Use Graph Parser for code structure
            if not file_name.endswith((".pdf", ".txt", ".md")):
                st.write(f"[{i+1}/{total_files}] Structural Code Analysis: {file_name}")
                parser.parse_file(file_path)
                full_context_summary.append(f"CODE: {file_name}")
            
            # Use PDF/Text extraction for documentation
            else:
                st.write(f"[{i+1}/{total_files}] Reading Documentation: {file_name}")
                if file_name.endswith(".pdf"):
                    content = extract_text_from_pdf(file_path)
                else:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                
                doc_id = f"DOC:{file_name}"
                parser.graph.add_node(doc_id, type="requirement_doc", content=content)
                full_context_summary.append(f"DOC: {file_name}")

        st.write("Constructing Vector Knowledge Base...")
        vector_store = CodeVectorStore(collection_name=st.session_state.session_id)
        vector_store.add_graph_documents(parser.graph)
        status.update(label="Analysis Complete!", state="complete", expanded=False)

    st.session_state.analysis_complete = True
    st.session_state.file_summary = full_context_summary
    st.session_state.node_count = parser.graph.number_of_nodes()
    st.session_state.edge_count = parser.graph.number_of_edges()
    st.rerun()

# --- RESULTS DISPLAY ---
if st.session_state.analysis_complete:
    st.divider()
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("Processed Project Assets")
        for item in st.session_state.file_summary:
            icon = "📜" if "CODE" in item else "📄"
            st.markdown(f"{icon} `{item.split(': ')[1]}`")
        
        if st.session_state.edge_count > 0:
            m1, m2 = st.columns(2)
            m1.metric("Graph Nodes", st.session_state.node_count)
            m2.metric("Code Dependencies", st.session_state.edge_count)
        else:
            st.success("✅ Knowledge Base Ready (Documentation-Only Mode)")

    with col2:
        st.subheader("AI Agent Generation")
        if st.button("Generate Test Scenarios"):
            vector_store = CodeVectorStore(collection_name=st.session_state.session_id)
            llm = LLMClient(model_name=model_name)
            final_report = ""
            
            progress_bar = st.progress(0)
            status_box = st.empty()
            
            files = st.session_state.file_summary
            total_files = len(files)
            
            # Dynamic Feature Header
            p_name = files[0].split(": ")[1].split(".")[0] if files else "Project"
            final_report += f"Feature: Automated Tests for {p_name}\n\n"
            
            for i, f in enumerate(files):
                fname = f.split(": ")[1]
                status_box.info(f"Processing Logic: `{fname}` ({i+1}/{total_files})")
                
                query = f"Analyze structural logic of {fname} and generate Gherkin scenarios."
                res = vector_store.search_similar(query, k=3)
                
                if res['documents']:
                    context = "\n".join(res['documents'][0])
                    meta = str(res['metadatas'][0])
                    out = llm.generate_response(context, meta, query)
                    final_report += f"# --- Source: {fname} ---\n{out}\n\n"
                
                progress_bar.progress((i+1)/total_files)
            
            status_box.success(f"Generation Complete: {total_files} components analyzed.")
            
            st.markdown("### 📝 Generated Gherkin Feature Set")
            st.code(final_report, language="gherkin") # Copy button is automatic here
            st.download_button("Download .feature File", final_report, "comprehensive_tests.feature")