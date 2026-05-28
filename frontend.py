```python
import streamlit as st
import requests

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="NeuralPaper AI",
    page_icon="🧠",
    layout="wide"
)

# ---------------- BACKEND URL ---------------- #

API_URL = "https://YOUR_BACKEND_URL.onrender.com"

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #111827 45%,
        #020617 100%
    );
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero-title {
    font-size: 60px;
    font-weight: 700;
    color: white;
}

.gradient-text {
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: #94a3b8;
    font-size: 18px;
    margin-bottom: 35px;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 18px;
    margin-bottom: 25px;
    border: 1px solid rgba(255,255,255,0.08);
}

.section-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 18px;
    color: #60a5fa;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 14px;
    font-size: 16px;
    font-weight: 600;
}

.stButton > button:hover {
    opacity: 0.92;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HERO ---------------- #

st.markdown("""
<div class="hero-title">
NeuralPaper <span class="gradient-text">AI</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="subtitle">
AI-powered research paper assistant using FastAPI, Groq, and Streamlit.
</div>
""", unsafe_allow_html=True)

# ---------------- INPUT TABS ---------------- #

tab1, tab2 = st.tabs(["ArXiv URL", "Upload PDF"])

pdf_url = None
uploaded_file = None

with tab1:

    pdf_url = st.text_input(
        "Enter ArXiv PDF URL",
        placeholder="https://arxiv.org/pdf/2401.02385.pdf"
    )

with tab2:

    uploaded_file = st.file_uploader(
        "Upload Research Paper",
        type=["pdf"]
    )

# ---------------- GENERATE BUTTON ---------------- #

if st.button("Generate AI Analysis"):

    st.info("Large papers may take 1-3 minutes.")

    try:

        # ---------- URL FLOW ---------- #

        if pdf_url:

            response = requests.post(
                f"{API_URL}/summarize_url/",
                json={"url": pdf_url},
                timeout=3600
            )

        # ---------- FILE FLOW ---------- #

        elif uploaded_file:

            files = {
                "file": uploaded_file
            }

            response = requests.post(
                f"{API_URL}/upload_pdf/",
                files=files,
                timeout=3600
            )

        else:

            st.warning("Please upload a PDF or provide an ArXiv URL.")
            st.stop()

        # ---------- RESPONSE ---------- #

        if response.status_code == 200:

            data = response.json()

            if "error" in data:

                st.error(data["error"])

            else:

                # ---------- SUMMARY ---------- #

                st.markdown("""
                <div class="section-title">
                Research Summary
                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    f"<div class='card'>{data['summary']}</div>",
                    unsafe_allow_html=True
                )

                # ---------- FLASHCARDS ---------- #

                st.markdown("""
                <div class="section-title">
                Flashcards
                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    f"<div class='card'>{data['flashcards']}</div>",
                    unsafe_allow_html=True
                )

                # ---------- QUIZ ---------- #

                st.markdown("""
                <div class="section-title">
                Quiz
                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    f"<div class='card'>{data['quiz']}</div>",
                    unsafe_allow_html=True
                )

                # ---------- DOWNLOAD ---------- #

                combined_output = f"""
SUMMARY

{data['summary']}

FLASHCARDS

{data['flashcards']}

QUIZ

{data['quiz']}
"""

                st.download_button(
                    label="Download Report",
                    data=combined_output,
                    file_name="neuralpaper_report.txt",
                    mime="text/plain"
                )

        else:

            st.error("Failed to process paper.")

    except Exception as e:

        st.error("Server error or timeout issue.")
```
