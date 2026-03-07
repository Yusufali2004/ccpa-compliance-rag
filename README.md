# ⚖️ CCPA Compliance RAG Engine
**Event:** OpenHack 2026 (IISc Bangalore) | **Team:** Algo Ninjas

A Hybrid Retrieval-Augmented Generation (RAG) system designed to automate the detection of CCPA (California Consumer Privacy Act) violations in business data practices.


## 🚀 Live Demo & Video
- **Live Dashboard:** [https://ccpa-compliance-rag-aa.streamlit.app/](https://ccpa-compliance-rag-aa.streamlit.app/)
- **LinkedIn Demo:** [LinkedIn Post](https://www.linkedin.com/posts/md-yusuf-ali-_openhack2026-iisc-algoninjas-activity-7434849210149163008-mVIT?utm_source=share&utm_medium=member_desktop&rcm=ACoAADodLfYBY_EZsUvRi6Nqo9dGHfrBOYTUpyA)

  
## 🏗️ System Architecture
The engine utilizes a **Multi-Layered Hybrid Pipeline** to balance high-speed deterministic checks with deep agentic reasoning:

1. **Rule-Based Analysis:** Instant detection of high-risk patterns using regex and keyword logic (e.g., unauthorized sale of minor's data).
2. **Semantic RAG Layer:** - **Vector Store:** ChromaDB indexing the official CCPA Statute PDF.
   - **Embeddings:** `all-MiniLM-L6-v2` for semantic mapping of legal text.
3. **Agentic Reasoning:** Powered by **Qwen-2.5-7B-Instruct** via Hugging Face Inference API to interpret complex legal nuances and statutes.
4. **Deterministic Output:** Strict Pydantic validation ensuring standardized `{"harmful": bool, "articles": []}` schema compliance.

## 🛠️ Tech Stack
- **AI/ML:** Qwen-2.5-7B, ChromaDB, SentenceTransformers.
- **Backend:** FastAPI (Async Orchestration).
- **Frontend:** Streamlit (Real-time Compliance Dashboard).
- **Deployment:** GitHub & Streamlit Cloud.

## 🧪 Complexity Analysis
- **Time Complexity:** $O(K \log N)$ for vector retrieval, where $N$ is the number of law chunks.
- **Efficiency:** Hybrid execution reduces LLM latency by resolving common patterns through the rule-based layer first.

## ⚙️ Setup & Installation
1. Clone the repo: `git clone https://github.com/Yusufali2004/ccpa-compliance-rag.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set your `HF_TOKEN` in a local `.env` file or Streamlit Secrets.
4. Launch Application:
To run the full hybrid system locally, open two terminals:

Terminal 1 (Backend API):

```bash
python -m uvicorn main:app --port 8000
```

Terminal 2 (Frontend UI):

```bash
streamlit run app.py
````

## 👥 Team Algo Ninjas
- **Md Yusuf Ali:** Chief AI Architect & Backend Lead
- **Md Irfan Ahmed:** Frontend Engineer
- **Mohammad Arif Siddiq:** Data Engineer
