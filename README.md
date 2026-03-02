# ⚖️ CCPA Compliance RAG Engine

An entirely local, highly-optimized Retrieval-Augmented Generation (RAG) API built to analyze business data practices for California Consumer Privacy Act (CCPA) compliance. 

Powered by **Qwen-2.5-7B-Instruct** (quantized to 4-bit) and **ChromaDB**, packaged perfectly into a single Docker container.

## 🚀 Architecture Highlights
* **100% Local Inference:** No external OpenAI API calls. The 7-Billion parameter LLM runs entirely within the Docker container.
* **Smart RAG Pipeline:** Uses `SentenceTransformers` (`all-MiniLM-L6-v2`) and ChromaDB to chunk and semantically retrieve relevant CCPA statutes from the official PDF.
* **Memory Safe:** Implements strict context-window truncation to prevent CUDA Out-Of-Memory (OOM) crashes on consumer GPUs.
* **Strict JSON Enforcement:** API strictly enforces the requested JSON schema (`harmful: bool`, `articles: List[str]`) using FastAPI and Pydantic validation.
* **Rubric Compliant:** Model weights are baked into the image at *build time*, and the Hugging Face token is passed securely via build arguments, ensuring lightning-fast boot times without hardcoded secrets.

---

## 🛠️ How to Build and Run

### 1. Build the Docker Image
To comply with security requirements, the Hugging Face token is passed as a build argument. The Dockerfile processes the CCPA PDF and bakes the 14GB LLM weights directly into the image so inference can start immediately.

```bash
docker build --build-arg HF_TOKEN="your_huggingface_token" -t ccpa-compliance-api .