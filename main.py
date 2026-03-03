import os
import json
import re
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load local .env if it exists
load_dotenv()

app = FastAPI()

# --- Secure HF Token Loading ---
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

# Initialize client only if token is present
hf_client = None
if HF_TOKEN:
    hf_client = InferenceClient(model=MODEL_NAME, token=HF_TOKEN)

# --- Load ChromaDB safely ---
client = chromadb.PersistentClient(path="./ccpa_db")
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

try:
    collection = client.get_collection(name="ccpa_statutes", embedding_function=embed_fn)
except Exception:
    collection = None

class AnalyzeRequest(BaseModel):
    prompt: str

class AnalyzeResponse(BaseModel):
    harmful: bool
    articles: List[str]

@app.get("/health")
def health():
    return {"status": "ok", "db_loaded": collection is not None, "llm_ready": hf_client is not None}

# Core Logic: Deterministic Rules
def rule_based_analysis(text: str):
    t = text.lower()
    if "sell" in t and "without" in t and ("inform" in t or "notice" in t):
        return True, ["Section 1798.120"]
    if "sell" in t and ("without" in t or "not inform" in t or "without notifying" in t):
        return True, ["Section 1798.100", "Section 1798.120"]
    if ("collect" in t) and "privacy policy" in t and ("not mention" in t or "doesn't mention" in t):
        return True, ["Section 1798.100"]
    if ("delete" in t) and ("ignore" in t or "keeping all records" in t):
        return True, ["Section 1798.105"]
    if "higher price" in t and "opt out" in t:
        return True, ["Section 1798.125"]
    if ("14-year" in t or "under 16" in t or "minor" in t) and "without" in t and "consent" in t:
        return True, ["Section 1798.120"]
    if "clear privacy policy" in t and "opt out" in t:
        return False, []
    if "deleted all personal data within 45 days" in t:
        return False, []
    if "do not sell my personal information" in t:
        return False, []
    if "equal service and pricing" in t:
        return False, []
    return None, None

# Core Logic: LLM RAG Fallback
def llm_analysis(prompt: str):
    if not hf_client or not collection:
        return False, ["Error: AI services not initialized"]
    try:
        results = collection.query(query_texts=[prompt], n_results=3)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        context = ""
        for doc, meta in zip(docs, metas):
            section = meta.get("article", "Unknown Section")
            context += f"[{section}] {doc[:800]}\n\n"

        full_prompt = f"Return ONLY JSON: {{\"harmful\": bool, \"articles\": []}}\n\nSTATUTES:\n{context}\n\nUSER:{prompt}"
        response = hf_client.text_generation(full_prompt, max_new_tokens=200, temperature=0.1)
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if not match: return False, []
        parsed = json.loads(match.group(0))
        return parsed.get("harmful", False), parsed.get("articles", [])
    except Exception as e:
        return False, [f"Analysis Error: {str(e)}"]

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    harmful, articles = rule_based_analysis(request.prompt)
    if harmful is None:
        harmful, articles = llm_analysis(request.prompt)
    return AnalyzeResponse(harmful=harmful, articles=articles)