import requests
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings

# =========================
# CONFIG
# =========================
DB_PATH = "embeddings/faiss_index"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:mini"

# =========================
# LOAD EMBEDDINGS + VECTOR DB
# =========================
embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vector_db = FAISS.load_local(
    DB_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

# =========================
# CALL PHI-3 VIA OLLAMA API
# =========================
def call_phi3(prompt: str) -> str:
    payload = {
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=120
        )
        response.raise_for_status()

        data = response.json()

        # VERY IMPORTANT: always return a string
        return data.get("response", "").strip()

    except Exception as e:
        print("ERROR IN call_phi3:", e)
        return "The mentor is temporarily unavailable. Please try again."


# =========================
# RAG RESPONSE
# =========================
def get_rag_response(user_question: str) -> str:
    docs = vector_db.similarity_search(user_question, k=3)

    context = "\n\n".join(doc.page_content for doc in docs)

    prompt = f"""
You are an experienced college mentor.

STRICT FORMAT RULES:
- Use clear bullet points
- Each bullet must be short (1–2 lines max)
- Use headings like Week 1, Week 2 if roadmap
- Do NOT write paragraphs
- Separate bullets with line breaks

Context:
{context}

Question:
{user_question}

Answer (bullet points only):
"""

    return call_phi3(prompt)
