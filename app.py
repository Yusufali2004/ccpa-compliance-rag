import streamlit as st
import requests
import time

# ---------------------------
# Configuration
# ---------------------------
API_BASE = "http://localhost:8000"
API_ANALYZE = f"{API_BASE}/analyze"
API_HEALTH = f"{API_BASE}/health"

st.set_page_config(
    page_title="CCPA Compliance Engine",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ AI-Powered CCPA Compliance Engine")
st.markdown("Analyze business practices against California Consumer Privacy Act (CCPA) statutes.")

st.divider()

# ---------------------------
# Backend Health Check
# ---------------------------
try:
    health = requests.get(API_HEALTH, timeout=3)
    if health.status_code == 200:
        st.success("🟢 Backend Connected")
    else:
        st.warning("🟡 Backend responding unexpectedly")
except:
    st.error("🔴 Backend not running. Start FastAPI first.")
    st.stop()

# ---------------------------
# Input Box
# ---------------------------
practice = st.text_area(
    "Enter a Business Practice to Analyze:",
    height=150,
    placeholder="Example: We sell user data to advertisers without opt-out options..."
)

# ---------------------------
# Submit Button
# ---------------------------
if st.button("Analyze Compliance Engine", type="primary", use_container_width=True):

    if not practice.strip():
        st.warning("⚠️ Please enter a business practice to analyze.")
    else:
        start_time = time.time()

        with st.spinner("🧠 Running Compliance Analysis..."):
            try:
                response = requests.post(
                    API_ANALYZE,
                    json={"prompt": practice},
                    timeout=120
                )

                if response.status_code == 200:
                    end_time = time.time()
                    result = response.json()

                    harmful = result.get("harmful", False)
                    articles = result.get("articles", [])

                    st.divider()
                    st.subheader("📊 Analysis Report")

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        if harmful:
                            st.error("🚨 CCPA VIOLATION DETECTED")
                            if articles:
                                st.markdown("Violated Sections:")
                                for a in articles:
                                    st.markdown(f"- {a}")
                            else:
                                st.markdown("Violation detected but no specific section returned.")
                        else:
                            st.success("✅ FULLY COMPLIANT")
                            st.markdown("No CCPA violations detected.")

                    with col2:
                        st.metric(
                            label="Inference Time",
                            value=f"{round(end_time - start_time, 2)} sec"
                        )
                        st.metric(
                            label="Processing Mode",
                            value="RAG + HF Inference"
                        )

                    with st.expander("🛠 Raw API JSON"):
                        st.json(result)

                else:
                    st.error(f"❌ API Error {response.status_code}")
                    st.code(response.text)

            except requests.exceptions.Timeout:
                st.error("⏳ Request timed out. Model may still be loading.")

            except requests.exceptions.ConnectionError:
                st.error("🔴 Cannot connect to backend.")

            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")