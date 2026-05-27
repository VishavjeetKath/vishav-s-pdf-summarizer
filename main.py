import os
import logging
import requests
import fitz
import httpx

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------- CONFIG ---------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- REQUEST MODEL ---------------- #

class URLRequest(BaseModel):
    url: str

# ---------------- HEALTH CHECK ---------------- #

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Backend is running"
    }

# ---------------- MAIN ROUTE ---------------- #

@app.post("/summarize_arxiv/")
async def summarize_arxiv(request: URLRequest):

    try:

        url = request.url

        logger.info(f"Downloading PDF from {url}")

        pdf_path = download_pdf(url)

        if not pdf_path:
            return {"error": "Failed to download PDF"}

        text = extract_text_from_pdf(pdf_path)

        if not text:
            return {"error": "No text extracted from PDF"}

        summary = await summarize_text(text)

        return {"summary": summary}

    except Exception as e:

        logger.error(str(e))

        return {"error": str(e)}

# ---------------- DOWNLOAD PDF ---------------- #

def download_pdf(url):

    try:

        if not url.startswith("https://arxiv.org/pdf/"):
            return None

        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            return None

        pdf_path = "paper.pdf"

        with open(pdf_path, "wb") as f:
            f.write(response.content)

        return pdf_path

    except Exception as e:

        logger.error(str(e))
        return None

# ---------------- EXTRACT TEXT ---------------- #

def extract_text_from_pdf(pdf_path):

    try:

        doc = fitz.open(pdf_path)

        text = ""

        for page in doc:
            text += page.get_text()

        return text

    except Exception as e:

        logger.error(str(e))
        return ""

# ---------------- SUMMARIZE TEXT ---------------- #

async def summarize_text(text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=12000,
        chunk_overlap=500
    )

    chunks = splitter.split_text(text)

    logger.info(f"Created {len(chunks)} chunks")

    chunk_summaries = []

    for i, chunk in enumerate(chunks):

        logger.info(f"Processing chunk {i+1}")

        summary = await summarize_chunk(chunk)

        chunk_summaries.append(summary)

    combined_summary = "\n\n".join(chunk_summaries)

    final_prompt = f"""
    Create a structured technical summary of this research paper.

    Organize the summary into:
    1. Overview
    2. Methodology
    3. Architecture
    4. Results
    5. Key Insights

    Content:
    {combined_summary}
    """

    final_summary = await groq_chat(final_prompt)

    return final_summary

# ---------------- SUMMARIZE CHUNK ---------------- #

async def summarize_chunk(chunk):

    prompt = f"""
    Extract important technical details from the following content.

    Focus on:
    - algorithms
    - implementation
    - architecture
    - datasets
    - benchmarks
    - results
    - optimization techniques

    Content:
    {chunk}
    """

    return await groq_chat(prompt)

# ---------------- GROQ API ---------------- #

async def groq_chat(prompt):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }

    async with httpx.AsyncClient(timeout=300) as client:

        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:

            logger.error(response.text)

            return "Failed to generate summary"

        data = response.json()

        return data["choices"][0]["message"]["content"]

# ---------------- RUN SERVER ---------------- #

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=10000
    )
