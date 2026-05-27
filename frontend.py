import streamlit as st
import requests

st.set_page_config(
    page_title="NeuralPaper AI",
    page_icon="🧠",
    layout="wide"
)

# ---------- CUSTOM CSS ----------
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

.main-container {
    padding-top: 40px;
    padding-bottom: 40px;
}

.hero-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    border-radius: 24px;
    padding: 48px;
    margin-bottom: 30px;
}

.hero-title {
    font-size: 64px;
    font-weight: 700;
    line-height: 1.05;
    margin-bottom: 16px;
    color: white;
}

.gradient-text {
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 18px;
    line-height: 1.7;
    margin-bottom: 28px;
    max-width: 700px;
}

.stTextInput > div > div > input {
    background-color: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    color: white;
    border-radius: 16px;
    padding: 18px;
    font-size: 16px;
}

.stTextInput > div > div > input:focus {
    border: 1px solid #60a5fa;
    box-shadow: none;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 14px 22px;
    font-size: 17px;
    font-weight: 600;
    transition: 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    opacity: 0.92;
}

.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 24px;
    text-align: center;
}

.metric-title {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: white;
}

.summary-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 22px;
}

.summary-title {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 16px;
    color: #60a5fa;
}

.summary-content {
    color: #d1d5db;
    line-height: 1.9;
    font-size: 16px;
}

.footer-note {
    color: #64748b;
    text-align: center;
    margin-top: 50px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ---------- HERO ----------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown("""
<div class="hero-box">
    <div class="hero-title">
        AI Research <span class="gradient-text">Summarizer</span>
    </div>

    <div class="hero-subtitle">
        Transform complex research papers into structured technical summaries using
        Ollama, Gemma 3, FastAPI, and Streamlit.
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- METRICS ----------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Model</div>
        <div class="metric-value">Gemma 3</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Backend</div>
        <div class="metric-value">FastAPI</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Processing</div>
        <div class="metric-value">Parallel</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- INPUT ----------
pdf_url = st.text_input(
    "ArXiv PDF URL",
    placeholder="https://arxiv.org/pdf/2401.02385.pdf"
)

# ---------- SUMMARY FUNCTION ----------
def render_summary_section(title, content):
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-title">{title}</div>
        <div class="summary-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- BUTTON ----------
if st.button("Generate Technical Summary"):
    if pdf_url:

        with st.spinner("Analyzing research paper..."):

            try:
                response = requests.post(
                    "http://localhost:8000/summarize_arxiv/",
                    json={"url": pdf_url},
                    timeout=3600
                )

                if response.status_code == 200:

                    data = response.json()

                    if "error" in data:
                        st.error(data["error"])

                    else:
                        summary = data.get("summary", "")

                        st.success("Summary generated successfully.")

                        sections = summary.split("#")[1:]

                        for section in sections:

                            if section.strip():

                                parts = section.split("\n", 1)

                                if len(parts) == 2:
                                    title, content = parts

                                    render_summary_section(
                                        title.strip(),
                                        content.strip()
                                    )

                        st.download_button(
                            label="Download Summary",
                            data=summary,
                            file_name="research_summary.md",
                            mime="text/markdown"
                        )

                else:
                    st.error("Failed to process the paper.")

            except Exception as e:
                st.error(f"Error: {str(e)}")

    else:
        st.warning("Please enter a valid ArXiv PDF URL.")

# ---------- FOOTER ----------
st.markdown("""
<div class="footer-note">
Built with Streamlit · FastAPI · Ollama · LangChain
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
