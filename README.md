# 🧠 QA Expert AI: Neuro-Symbolic Test Engineering Agent

QA Expert AI is a production-ready testing solution that bridges the gap between **Natural Language Requirements (PDF)** and **Multi-Language Source Code**. Built on a Neuro-Symbolic RAG architecture, it builds a structural Knowledge Graph of your ecosystem and generates consolidated, high-fidelity **Gherkin Test Scenarios**.

## 🚀 Key Features

* **Global Logic Consolidation**: Automatically synthesizes scenarios from multiple files, eliminating overlaps while preserving critical business rules.
* **Neuro-Symbolic RAG**: Combines AST-based structural parsing with semantic vector search for deep context awareness.
* **Multi-Language Source Analysis**: Native support for Python, Java, JavaScript, C++, TypeScript, Go, and more.
* **Industrial Requirement Extraction**: Directly maps constraints and thresholds from technical PDFs to Gherkin scenarios.
* **Smart Filtering**: Automatically ignores `README.md`, media files, and build artifacts (`node_modules`, `venv`, etc.).
* **Flexible Data Ingestion**: Supports direct file uploads, ZIP archives, and Local Directory scanning.

## 🛠️ Tech Stack

* **UI Framework**: Streamlit
* **LLM Orchestration**: Ollama (Local LLM), LangChain
* **Vector Database**: ChromaDB (Dynamic Session-based)
* **Graph Engine**: NetworkX, Tree-Sitter
* **Document Analysis**: PyMuPDF (fitz)

## 📦 Installation & Setup

### 1. Clone & Navigate
```bash
git clone [https://github.com/metindeder/QA-Expert-AI.git](https://github.com/metindeder/QA-Expert-AI.git)
cd QA-Expert-AI
```

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Custom Local LLM Setup (Ollama & Hugging Face)
This project uses a custom-trained model specifically fine-tuned for QA Engineering and Gherkin scenario generation.

**Step A: Download the Model**
Download the fine-tuned GGUF model from Hugging Face:
👉 **[Llama-3-Gherkin-QA-Expert (Hugging Face)](https://huggingface.co/metindeder/Llama-3-Gherkin-QA-Expert)**

Place the downloaded `.gguf` file (e.g., `llama-3-8b-instruct.Q4_K_M.gguf`) into your project root directory.

**Step B: Create the Modelfile**
Ensure you have a file named `Modelfile` in your project root with the following content:
```dockerfile
FROM ./llama-3-8b-instruct.Q4_K_M.gguf

# EĞİTİM FORMATI (ALPACA)
TEMPLATE """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{{ .System }}

### Input:
{{ .Prompt }}

### Response:
"""

# SYSTEM MESAJI
SYSTEM """You are an expert Senior QA Engineer. Your task is to analyze the given requirements or code snippet (Input).
1. First, perform a detailed ANALYSIS: Identify variables, business rules, and boundary values.
2. Then, generate a comprehensive Gherkin feature file covering Happy Path, Negative Path, and Edge Cases.
"""

# Ayarlar
PARAMETER stop "### Instruction:"
PARAMETER stop "### Input:"
PARAMETER stop "### Response:"
PARAMETER stop "<|end_of_text|>"
PARAMETER temperature 0.1
PARAMETER num_ctx 4096
```

**Step C: Build and Run in Ollama**
Make sure [Ollama](https://ollama.ai/) is installed and running on your system, then build the custom model:
```bash
ollama create gherkin-qa -f Modelfile
```

## 💻 Usage

1.  **Launch Dashboard:** `streamlit run app.py`
2.  **Input Method:** Use **Upload** for individual assets or **Local Path** to scan your entire repository.
3.  **Analyze**: Click **"Start Project Analysis"** to build the Knowledge Graph.
4.  **Consolidate**: Choose your strategy and click **"Generate Test Scenarios"** to produce your test suite.

## 📸 Screenshots

<p align="center">
  <img src="screenshots/1.jpeg" width="32%" title="Upload & Configuration">
  <img src="screenshots/2.jpeg" width="32%" title="Project Analysis">
  <img src="screenshots/3.jpeg" width="32%" title="Dual-Mode Generation">
</p>
<p align="center">
  <img src="screenshots/4.jpeg" width="32%" title="Component-Wise Output">
  <img src="screenshots/7.jpeg" width="32%" title="Graph Nodes & Edges">
  <img src="screenshots/6.jpeg" width="32%" title="Master Test Suite">
</p>
<p align="center">
  <img src="screenshots/5.jpeg" width="32%" title="Global Consolidation">
  <img src="screenshots/8.jpeg" width="32%" title="Code Dependencies">
  <img src="screenshots/9.jpeg" width="32%" title="Final Gherkin Export">
</p>

## 📂 Project Structure

```text
.
├── app.py              # Main GUI and Orchestration logic
├── src/
│   ├── graph/          # AST Parsing (Symbolic Logic)
│   ├── rag/            # Vector Search (Neural Retrieval)
│   ├── agent/          # LLM QA Clients
│   └── utils/          # Document extraction utilities
├── data/
│   └── vector_db/      # Persistent Session storage
├── Modelfile           # Custom QA System Prompt
└── requirements.txt    # Library dependencies
```

---
**Maintained by**: [Metin - Fırat University Computer Engineering]
