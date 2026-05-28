```python
import os
import uuid
import fitz
import httpx
import requests

from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from langchain_text_splitters import RecursiveCharacterTextSplitter

# ---------------- LOAD ENV ---------------- #

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- FASTAPI ---------------- #

app = FastAPI(title="NeuralPaper AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- REQUEST MODEL ---------------- #

class URLRequest(BaseModel):
    url: str

# ---------------- HEALTH ---------------- #

@app.get("/health")
def health():
    return {"status": "running"}

# ---------------- URL ROUTE ---------------- #

@app.post("/summarize_url/")
async def summarize_url(request: URLRequest):

    pdf_path = download_pdf(request.url)

    if not pdf_path:
        return {"error": "Invalid arXiv URL"}

    text = extract_text(pdf_path)

    os.remove(pdf_path)

    return await generate_complete_response(text)

# ---------------- FILE ROUTE ---------------- #

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):

    file_id = f"{uuid.uuid4()}.pdf"

    with open(file_id, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_id)

    os.remove(file_id)

    return await generate_complete_response(text)

# ---------------- DOWNLOAD PDF ---------------- #

def download_pdf(url):

    try:

        response = requests.get(url)

        if response.status_code != 200:
            return None

        file_name = f"{uuid.uuid4()}.pdf"

        with open(file_name, "wb") as f:
            f.write(response.content)

        return file_name

    except:
        return None

# ---------------- EXTRACT TEXT ---------------- #

def extract_text(pdf_path):

    text = ""

    doc = fitz.open(pdf_path)

    for page in doc:
        text += page.get_text()

    return text

# ---------------- CHUNKING ---------------- #

def chunk_text(text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=500
    )

    return splitter.split_text(text)

# ---------------- MAIN AI RESPONSE ---------------- #

async def generate_complete_response(text):

    chunks = chunk_text(text)

    summaries = []

    for chunk in chunks:

        prompt = f"""
        Extract important technical details from this research paper chunk.

        Focus on:
        - methodology
        - architecture
        - datasets
        - results
        - innovations

        Content:
        {chunk}
        """

        result = await groq_chat(prompt)

        summaries.append(result)

    combined = "\n".join(summaries)

    # ---------- FINAL SUMMARY ---------- #

    final_prompt = f"""
    Create a structured research summary.

    Use these sections:

    # Overview
    # Methodology
    # Architecture
    # Results
    # Key Insights

    Content:
    {combined}
    """

    summary = await groq_chat(final_prompt)

    # ---------- FLASHCARDS ---------- #

    flashcard_prompt = f"""
    Generate 10 flashcards from this research paper.

    Format:
    Q:
    A:

    Content:
    {combined}
    """

    flashcards = await groq_chat(flashcard_prompt)

    # ---------- QUIZ ---------- #

    quiz_prompt = f"""
    Generate 10 technical MCQs from this research paper.

    Include:
    - question
    - 4 options
    - correct answer

    Content:
    {combined}
    """

    quiz = await groq_chat(quiz_prompt)

    return {
        "summary": summary,
        "flashcards": flashcards,
        "quiz": quiz
    }

# ---------------- GROQ ---------------- #

async def groq_chat(prompt):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
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

        data = response.json()

        return data["choices"][0]["message"]["content"]

# ---------------- RUN ---------------- #

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=10000
    )
```
