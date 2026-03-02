# ⚖️ CCPA Compliance RAG Engine
**Team:** Algo Ninjas | **Event:** OpenHack 2026 (IISc Bangalore)

A Hybrid Retrieval-Augmented Generation (RAG) system designed to automate the detection of CCPA (California Consumer Privacy Act) violations in business data practices.

## 🚀 System Architecture
The engine utilizes a **Multi-Layered Pipeline** to balance high-speed deterministic checks with deep agentic reasoning.

1. **Rule-Based Analysis:** Instant detection of high-risk patterns (e.g., unauthorized sale of minor's data without parental consent).
2. **Semantic RAG Layer:** - **Vector Store:** ChromaDB indexing the official CCPA Statute PDF.
   - **Embeddings:** `all-MiniLM-L6-v2` generating semantic maps of legal text.
3. **Agentic Reasoning:** Powered by **Qwen-2.5-7B-Instruct** via Hugging Face Inference API for interpreting complex legal nuance.
4. **Deterministic Output:** Strict Pydantic validation ensuring `{"harmful": bool, "articles": []}` schema compliance.

## 🛠️ Tech Stack
- **Backend:** FastAPI (Async Orchestration).
- **Frontend:** Streamlit (Real-time Compliance Dashboard).
- **Database:** ChromaDB (Persistent Vector Store).
- **LLM:** Qwen-2.5-7B (Quantized Inference).

## 🧪 Complexity Analysis
- **Time Complexity:** $O(K \log N)$ for vector retrieval, where $N$ is the number of law chunks.
- **Architecture:** Hybrid (Local Vector Storage + Cloud Inference).

## ⚙️ Setup & Installation
1. Clone the repo: `git clone https://github.com/Yusufali2004/ccpa-compliance-rag.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set your `HF_TOKEN` in `.env` or Streamlit Secrets.
4. Launch app: `streamlit run app.py`

## 👥 Team Algo Ninjas
- **Md Yusuf Ali:** Chief AI Architect & Backend Lead
- **Md Irfan:** Frontend Engineer
- **Mohammad Arif Siddiq:** Data Engineer