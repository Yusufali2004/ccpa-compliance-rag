import streamlit as st
import time
import os

# Import backend logic directly for "Single-Process" mode on Streamlit Cloud
from main import rule_based_analysis, llm_analysis

st.set_page_config(
    page_title="CCPA Compliance Engine",
    page_icon="⚖️",
    layout="wide"
)

# --- Check for Token ---
if not os.getenv("HF_TOKEN"):
    st.error("🔑 HF_TOKEN missing. Please add it to your .env file or Streamlit Secrets.")
    st.stop()

st.title("⚖️ AI-Powered CCPA Compliance Engine")
st.caption("Algo Ninjas | OpenHack 2026 Submission")
st.markdown("Analyze business practices against CCPA statutes using Hybrid RAG.")

st.divider()

# --- Input Box ---
practice = st.text_area(
    "Enter a Business Practice to Analyze:",
    height=150,
    placeholder="Example: We sell user data of 14-year-old minors without parental consent..."
)

if st.button("Analyze Compliance", type="primary", use_container_width=True):
    if not practice.strip():
        st.warning("⚠️ Please enter a business practice.")
    else:
        start_time = time.time()
        with st.spinner("🧠 Analyzing via Hybrid RAG Engine..."):
            # Step 1: Deterministic Rules
            harmful, articles = rule_based_analysis(practice)
            mode = "Deterministic Rules"

            # Step 2: Fallback to LLM if needed
            if harmful is None:
                harmful, articles = llm_analysis(practice)
                mode = "RAG + Qwen-2.5-7B"

            end_time = time.time()

            st.divider()
            st.subheader("📊 Analysis Report")

            col1, col2 = st.columns([2, 1])
            with col1:
                if harmful:
                    st.error("🚨 CCPA VIOLATION DETECTED")
                    for a in articles:
                        st.markdown(f"**Violated:** {a}")
                else:
                    st.success("✅ FULLY COMPLIANT")
                    st.markdown("No violations found in the provided text.")

            with col2:
                st.metric("Inference Time", f"{round(end_time - start_time, 2)}s")
                st.metric("Processing Mode", mode)

            with st.expander("🛠 Architecture Details"):
                st.write(f"**Database:** ChromaDB (Local)")
                st.write(f"**LLM:** Qwen-2.5-7B-Instruct (Cloud)")