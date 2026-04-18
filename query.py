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


def answer_question(question: str) -> tuple[str, list[str]]:
    """
    Returns (answer, [source_filenames])
    """
    vs = get_vectorstore()
    results = vs.similarity_search(question, k=TOP_K)

    if not results:
        return "I couldn't find relevant information in FAU's policies.", []

    # Build context from retrieved chunks
    context_parts = []
    sources = []
    for doc in results:
        filename = doc.metadata.get("filename", "Unknown")
        category = doc.metadata.get("category", "")
        context_parts.append(f"[Source: {filename} ({category})]\n{doc.page_content}")
        if filename not in sources:
            sources.append(filename)

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""You are PolicyOwl, an AI assistant that helps FAU (Florida Atlantic University) students find accurate information about university policies, academics, and campus life.

Answer the student's question using ONLY the policy excerpts provided below. Be concise and helpful. If the answer isn't in the excerpts, say so honestly.

Always mention which policy or source your answer comes from.

POLICY EXCERPTS:
{context}

STUDENT QUESTION: {question}

ANSWER:"""

    client = get_client()
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    answer = message.content[0].text
    return answer, sources


if __name__ == "__main__":
    print("PolicyOwl Query Test")
    print("=" * 40)
    test_questions = [
        "What is FAU's policy on acceptable use of technology?",
        "When is the last day to drop a class?",
        "What are the dining options on campus?",
        "What is FAU's policy on artificial intelligence?",
    ]
    for q in test_questions:
        print(f"\nQ: {q}")
        answer, sources = answer_question(q)
        print(f"A: {answer[:300]}...")
        print(f"Sources: {sources}")
