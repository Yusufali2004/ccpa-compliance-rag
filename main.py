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

# ---------------------------
# Load .env file
# ---------------------------
load_dotenv()

app = FastAPI()

# ---------------------------
# Secure HF Token Loading
# ---------------------------
HF_TOKEN = os.getenv("HF_TOKEN")

# Fallback to the provided token if .env is missing
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in environment variables!")

MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
hf_client = InferenceClient(
    model=MODEL_NAME,
    token=HF_TOKEN
)

# ---------------------------
# Load ChromaDB (Local RAG Storage)
# ---------------------------
# This matches the folder you need to upload to GitHub
client = chromadb.PersistentClient(path="./ccpa_db")

embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_collection(
    name="ccpa_statutes",
    embedding_function=embed_fn
)

# ---------------------------
# Request / Response Models
# ---------------------------
class AnalyzeRequest(BaseModel):
    prompt: str

class AnalyzeResponse(BaseModel):
    harmful: bool
    articles: List[str]

# ---------------------------
# Health Endpoint
# ---------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------
# Deterministic Rules (Fast Logic)
# ---------------------------
def rule_based_analysis(text: str):
    t = text.lower()

    # Rule: Selling data without notice
    if "sell" in t and "without" in t and ("inform" in t or "notice" in t):
        return True, ["Section 1798.120"]

    # Rule: Selling without notification (Broad)
    if "sell" in t and ("without" in t or "not inform" in t or "without notifying" in t):
        return True, ["Section 1798.100", "Section 1798.120"]

    # Rule: Silent collection not in policy
    if ("collect" in t) and "privacy policy" in t and ("not mention" in t or "doesn't mention" in t):
        return True, ["Section 1798.100"]

    # Rule: Denying deletion requests
    if ("delete" in t) and ("ignore" in t or "keeping all records" in t):
        return True, ["Section 1798.105"]

    # Rule: Discrimination for opting out
    if "higher price" in t and "opt out" in t:
        return True, ["Section 1798.125"]

    # Rule: Underage consent violations
    if ("14-year" in t or "under 16" in t or "minor" in t) and "without" in t and "consent" in t:
        return True, ["Section 1798.120"]

    # Compliant patterns
    if "clear privacy policy" in t and "opt out" in t:
        return False, []

    if "deleted all personal data within 45 days" in t:
        return False, []

    if "do not sell my personal information" in t:
        return False, []

    if "equal service and pricing" in t:
        return False, []

    # If no rules match, we return None to signal the LLM fallback
    return None, None

# ---------------------------
# LLM Fallback (RAG Version)
# ---------------------------
def llm_analysis(prompt: str):
    try:
        if collection.count() == 0:
            return False, []

        # Step 1: Query local ChromaDB
        results = collection.query(query_texts=[prompt], n_results=3)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        if not docs:
            return False, []

        context = ""
        for doc, meta in zip(docs, metas):
            section = meta.get("article", "Unknown Section")
            context += f"[{section}] {doc[:800]}\n\n"

        # Step 2: Prompt Engineering for the Cloud LLM
        full_prompt = f"""You are a CCPA compliance engine. Analyze the USER QUERY against the STATUTES.
Return ONLY valid JSON:
{{
  "harmful": true or false,
  "articles": ["Section 1798.xxx"]
}}

STATUTES:
{context}

USER QUERY:
{prompt}
"""
        # Step 3: Cloud Inference
        response = hf_client.text_generation(
            full_prompt,
            max_new_tokens=200,
            temperature=0.1
        )

        # Step 4: Robust JSON Extraction
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if not match:
            return False, []

        parsed = json.loads(match.group(0))
        return parsed.get("harmful", False), parsed.get("articles", [])

    except Exception as e:
        print(f"⚠️ LLM Error: {e}")
        return False, []

# ---------------------------
# Main Analyze Endpoint (Hybrid Pipeline)
# ---------------------------
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    # Try deterministic rules first
    harmful, articles = rule_based_analysis(request.prompt)

    # If rules didn't find a match, use the LLM RAG fallback
    if harmful is None:
        harmful, articles = llm_analysis(request.prompt)

    return AnalyzeResponse(
        harmful=harmful,
        articles=articles
    )