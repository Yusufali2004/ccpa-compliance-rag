import streamlit as st
import time
import os

# Directly importing logic to support single-process cloud deployment
from main import rule_based_analysis, llm_analysis

st.set_page_config(
    page_title="CCPA Compliance Engine",
    page_icon="⚖️",
    layout="wide"
)

# --- Check for Secret Token ---
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    st.error("🔑 HF_TOKEN missing. Please add it to your Streamlit Cloud Secrets.")
    st.stop()

st.title("⚖️ AI-Powered CCPA Compliance Engine")
st.caption("Algo Ninjas | OpenHack 2026 Submission")
st.markdown("Analyze business practices against CCPA statutes using a Hybrid RAG pipeline.")

st.divider()

# --- Input Box ---
practice = st.text_area(
    "Enter a Business Practice to Analyze:",
    height=150,
    placeholder="Example: We sell user data to advertisers without providing an opt-out link..."
)

if st.button("Run Compliance Analysis", type="primary", use_container_width=True):
    if not practice.strip():
        st.warning("⚠️ Please enter a practice to analyze.")
    else:
        start_time = time.time()
        with st.spinner("🧠 Querying Hybrid RAG Pipeline..."):
            # Execute Hybrid Pipeline logic directly
            harmful, articles = rule_based_analysis(practice)
            mode = "Deterministic Rules"

            if harmful is None:
                harmful, articles = llm_analysis(practice)
                mode = "RAG + Qwen-2.5-7B Agent"

            end_time = time.time()

            st.divider()
            st.subheader("📊 Compliance Report")

            col1, col2 = st.columns([2, 1])
            with col1:
                if harmful:
                    st.error("🚨 POTENTIAL CCPA VIOLATION DETECTED")
                    if articles:
                        st.markdown("**Relevant Statutes:**")
                        for a in articles:
                            st.markdown(f"- {a}")
                else:
                    st.success("✅ COMPLIANCE VERIFIED")
                    st.markdown("No violations detected against existing CCPA vector data.")

            with col2:
                st.metric("Inference Latency", f"{round(end_time - start_time, 2)}s")
                st.metric("Analysis Tier", mode)

            with st.expander("🛠 System Telemetry"):
                st.write("**Vector Store:** ChromaDB (Persistent)")
                st.write("**LLM Hub:** Hugging Face Inference API")