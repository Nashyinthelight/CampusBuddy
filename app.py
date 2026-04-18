"""
app.py — PolicyOwl Streamlit UI
Run with: streamlit run app.py
"""

import streamlit as st
from query import get_answer

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PolicyOwl — FAU Policy Assistant",
    page_icon="🦉",
    layout="centered",
)

# ── FAU styling ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* FAU brand colors */
    :root {
        --fau-blue: #003366;
        --fau-red:  #CC0000;
    }

    /* Header bar */
    .owl-header {
        background: linear-gradient(135deg, #003366 0%, #004080 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .owl-header h1 { margin: 0; font-size: 2.4rem; }
    .owl-header p  { margin: 0.3rem 0 0; opacity: 0.85; font-size: 1rem; }

    /* Source badge */
    .source-badge {
        display: inline-block;
        background: #e8f0fe;
        color: #003366;
        border: 1px solid #c5d8f5;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin: 2px 3px 2px 0;
    }

    /* Sidebar example buttons */
    .stButton > button {
        width: 100%;
        text-align: left;
        background: #f0f4ff;
        border: 1px solid #c5d8f5;
        border-radius: 8px;
        color: #003366;
        font-size: 0.85rem;
        padding: 0.4rem 0.75rem;
    }
    .stButton > button:hover {
        background: #003366;
        color: white;
        border-color: #003366;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="owl-header">
    <h1>🦉 PolicyOwl</h1>
    <p>Your AI-Powered FAU Policy & Campus Assistant</p>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🦉 About PolicyOwl")
    st.markdown(
        "PolicyOwl answers questions about FAU's policies, academic deadlines, "
        "and campus resources — powered by RAG and the Claude AI."
    )
    st.divider()

    st.markdown("### 💡 Example Questions")

    st.markdown("**📚 Academics**")
    if st.button("When is the last day to drop a class?", key="ex1"):
        st.session_state.pending_question = "When is the last day to drop a class?"
    if st.button("What is the academic integrity policy?", key="ex2"):
        st.session_state.pending_question = "What is the academic integrity policy?"

    st.markdown("**🏫 Campus Life**")
    if st.button("What dining halls are on campus?", key="ex3"):
        st.session_state.pending_question = "What dining halls are on campus?"
    if st.button("Where is the tutoring center?", key="ex4"):
        st.session_state.pending_question = "Where is the tutoring center?"
    if st.button("What is FAU's tobacco policy?", key="ex5"):
        st.session_state.pending_question = "What is FAU's tobacco policy?"

    st.markdown("**📋 Deadlines & Policies**")
    if st.button("What is FAU's VPN policy?", key="ex6"):
        st.session_state.pending_question = "What is FAU's VPN policy?"
    if st.button("What do I do if I get a phishing email?", key="ex7"):
        st.session_state.pending_question = "What do I do if I get a phishing email?"
    if st.button("What is FAU's policy on weapons on campus?", key="ex8"):
        st.session_state.pending_question = "What is FAU's policy on weapons on campus?"

    st.divider()
    st.markdown(
        "<small>Answers are sourced from official FAU policy documents. "
        "Always verify critical information with the relevant FAU office.</small>",
        unsafe_allow_html=True,
    )

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            source_html = "".join(
                f'<span class="source-badge">📄 {s.replace(".txt","").replace(".pdf","").replace("_"," ")}</span>'
                for s in msg["sources"]
            )
            st.markdown(f"**Sources:** {source_html}", unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
# Pre-fill from sidebar button clicks
default_input = st.session_state.pop("pending_question", "") if st.session_state.pending_question else ""

question = st.chat_input("Ask a question about FAU policies, deadlines, or campus life...")

# Use sidebar-injected question if no manual input
if not question and default_input:
    question = default_input

if question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate answer
    with st.chat_message("assistant"):
        with st.spinner("Searching FAU policies..."):
            answer, sources = get_answer(question)

        st.markdown(answer)
        if sources:
            source_html = "".join(
                f'<span class="source-badge">📄 {s.replace(".txt","").replace(".pdf","").replace("_"," ")}</span>'
                for s in sources
            )
            st.markdown(f"**Sources:** {source_html}", unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
