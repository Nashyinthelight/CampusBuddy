"""
query.py — Retrieval + Claude API answer generation for PolicyOwl
"""

import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import anthropic

load_dotenv()

CHROMA_DIR = "chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5
MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are CampusBuddy 🦉, the official AI policy and campus assistant for Florida Atlantic University (FAU). You help students, faculty, and staff quickly find accurate answers about FAU policies, academic deadlines, campus resources, and university life.

YOUR BEHAVIOR:
- Answer questions using ONLY the policy excerpts and documents provided to you in each message.
- Always cite your source clearly. Use this format: "According to [Policy Name / Document Name], ..."
- If a question covers multiple policies, cite each one.
- If the answer is not found in the provided excerpts, say: "I don't have that information in my current policy database. I recommend contacting the relevant FAU office directly."
- Never make up information or answer from general knowledge — only use what's in the provided context.
- Be friendly, clear, and concise. Students are busy — get to the point.
- For deadlines, be specific with dates when they appear in the context.
- For policies, summarize the key rule first, then add detail if needed.

CATEGORIES YOU COVER:
1. Academics — drop deadlines, registration, graduation, academic integrity, grade appeals
2. Campus Life — dining, tutoring, IT policies, safety, alcohol/tobacco, housing
3. Deadlines & Policies — tuition due dates, registration windows, security policies, compliance

FAU SPIRIT: You are proud to be an FAU Owl. Keep responses helpful and professional."""

_vectorstore = None
_client = None


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        _vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
        )
    return _vectorstore


def get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


def get_answer(question: str) -> tuple[str, list[str]]:
    """
    Main entry point for app.py.
    Returns (answer_text, [source_filenames])
    """
    vs = get_vectorstore()
    results = vs.similarity_search(question, k=TOP_K)

    if not results:
        return (
            "I don't have that information in my current policy database. "
            "I recommend contacting the relevant FAU office directly.",
            [],
        )

    context_parts = []
    sources = []
    for doc in results:
        filename = doc.metadata.get("filename", "Unknown")
        category = doc.metadata.get("category", "")
        context_parts.append(f"[Source: {filename} | Category: {category}]\n{doc.page_content}")
        if filename not in sources:
            sources.append(filename)

    context = "\n\n---\n\n".join(context_parts)

    user_message = f"""Here are the relevant FAU policy excerpts for this question:

{context}

---

Student question: {question}"""

    client = get_client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text, sources


if __name__ == "__main__":
    print("PolicyOwl — Quick Test")
    print("=" * 50)
    tests = [
        "What is FAU's policy on acceptable use of technology?",
        "When is the last day to drop a class?",
        "What are the dining options on campus?",
        "What is FAU's policy on artificial intelligence?",
        "What is FAU's alcohol policy?",
    ]
    for q in tests:
        print(f"\nQ: {q}")
        answer, sources = get_answer(q)
        print(f"A: {answer[:400]}")
        print(f"Sources: {', '.join(sources)}")
        print("-" * 50)
