"""
app.py — CampusBuddy Streamlit UI
Run with: streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
from query import get_answer

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CampusBuddy — FAU Campus Assistant",
    page_icon="🦉",
    layout="wide",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Reset & base ── */
    [data-testid="stAppViewContainer"] { background: #f4f6fb; }
    [data-testid="stSidebar"] {
        background: #003366 !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2) !important; }

    /* ── Remove default top padding so banner sits flush ── */
    .block-container { padding-top: 0 !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    [data-testid="stHeader"] { display: none !important; }

    /* ── Full-width banner (normal flow, not fixed) ── */
    .banner {
        background: linear-gradient(120deg, #003366 0%, #004080 60%, #CC0000 100%);
        color: white;
        padding: 1rem 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin: -6rem -100vw 1.5rem -100vw;
        padding-left: calc(100vw - 100%);
        padding-right: calc(100vw - 100%);
        width: 200vw;
    }

    .banner-owl { font-size: 2.2rem; animation: owlBob 2s ease-in-out infinite; }
    .banner-text h1 { margin: 0; font-size: 1.6rem; font-weight: 800; letter-spacing: 1px; }
    .banner-text p  { margin: 0.15rem 0 0; opacity: 0.88; font-size: 0.85rem; }

    /* ── Owl bob (idle) ── */
    @keyframes owlBob {
        0%,100% { transform: translateY(0px) rotate(0deg); }
        25%      { transform: translateY(-6px) rotate(5deg); }
        75%      { transform: translateY(-3px) rotate(-4deg); }
    }

    /* ── Owl thinking spinner ── */
    .owl-thinking {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 1rem;
        background: white;
        border-radius: 12px;
        border-left: 4px solid #CC0000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .owl-thinking .spin-owl {
        font-size: 2rem;
        display: inline-block;
        animation: owlSpin 0.9s linear infinite;
    }
    .owl-thinking p { margin: 0; color: #003366; font-weight: 500; }
    @keyframes owlSpin {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* ── Chat messages ── */
    [data-testid="stChatMessage"] {
        background: white;
        border-radius: 14px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    }

    /* ── Source badges ── */
    .source-badge {
        display: inline-block;
        background: #eef2ff;
        color: #003366;
        border: 1px solid #c5d5f5;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.72rem;
        margin: 3px 3px 0 0;
        font-weight: 500;
    }

    /* ── Sidebar buttons ── */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        background: rgba(255,255,255,0.12) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 8px;
        color: white !important;
        font-size: 0.83rem;
        padding: 0.45rem 0.85rem;
        margin-bottom: 4px;
        transition: background 0.2s;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #CC0000 !important;
        border-color: #CC0000 !important;
    }

    /* ── Chat input ── */
    [data-testid="stChatInput"] textarea {
        border-radius: 12px !important;
        border: 2px solid #c5d5f5 !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #003366 !important;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Always show sidebar toggle button ── */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: #003366 !important;
        border-radius: 0 8px 8px 0 !important;
        color: white !important;
    }

    /* ── Content centering in wide layout ── */
    .block-container { max-width: 860px; margin: 0 auto; padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Full-width banner ─────────────────────────────────────────────────────────
st.markdown("""
<div class="banner">
    <div class="banner-owl">🦉</div>
    <div class="banner-text">
        <h1>CampusBuddy</h1>
        <p>Your AI-Powered FAU Policy &amp; Campus Assistant</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hey there, Owl! 🦉 I'm **CampusBuddy**, your AI-powered FAU campus assistant.\n\n"
                "I can help you with:\n"
                "- 📚 **Academics** — drop deadlines, registration, graduation requirements\n"
                "- 🏫 **Campus Life** — dining, tutoring, safety, IT policies\n"
                "- 📋 **Deadlines & Policies** — tuition, security, compliance\n\n"
                "Try clicking an example question on the left, or just ask me anything. Go Owls! 🔵🔴"
            ),
            "sources": [],
        }
    ]
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🦉 About CampusBuddy")
    st.markdown(
        "Ask anything about FAU policies, academic deadlines, "
        "and campus resources. Powered by RAG + Claude AI."
    )
    st.divider()

    st.markdown("### 💡 Example Questions")

    st.markdown("**📚 Academics**")
    if st.button("When is the last day to drop a class?", key="ex1"):
        st.session_state.pending_question = "When is the last day to drop a class?"
    if st.button("What is the academic integrity policy?", key="ex2"):
        st.session_state.pending_question = "What is the academic integrity policy?"
    if st.button("What are the graduation requirements?", key="ex3"):
        st.session_state.pending_question = "What are the graduation requirements?"

    st.markdown("**🏫 Campus Life**")
    if st.button("What dining halls are on campus?", key="ex4"):
        st.session_state.pending_question = "What dining halls are on campus?"
    if st.button("Where is the tutoring center?", key="ex5"):
        st.session_state.pending_question = "Where is the tutoring center?"
    if st.button("What is FAU's tobacco policy?", key="ex6"):
        st.session_state.pending_question = "What is FAU's tobacco policy?"

    st.markdown("**📋 Deadlines & Policies**")
    if st.button("What is FAU's VPN policy?", key="ex7"):
        st.session_state.pending_question = "What is FAU's VPN policy?"
    if st.button("What do I do if I get a phishing email?", key="ex8"):
        st.session_state.pending_question = "What do I do if I get a phishing email?"
    if st.button("What is FAU's policy on weapons on campus?", key="ex9"):
        st.session_state.pending_question = "What is FAU's policy on weapons on campus?"

    st.divider()
    st.markdown(
        "<small style='opacity:0.7'>Answers sourced from official FAU documents. "
        "Verify critical info with the relevant FAU office.</small>",
        unsafe_allow_html=True,
    )

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "🦉" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg.get("sources"):
            badges = "".join(
                f'<span class="source-badge">📄 {s.replace(".txt","").replace(".pdf","").replace("_"," ")}</span>'
                for s in msg["sources"]
            )
            st.markdown(f"**Sources:** {badges}", unsafe_allow_html=True)

# ── Collect input ─────────────────────────────────────────────────────────────
pending = st.session_state.pending_question
if pending:
    st.session_state.pending_question = ""

question = st.chat_input("Ask a question about FAU policies, deadlines, or campus life...")
if not question and pending:
    question = pending

# ── Handle question ───────────────────────────────────────────────────────────
if question:
    # User message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    # Animated owl while generating
    with st.chat_message("assistant", avatar="🦉"):
        placeholder = st.empty()
        placeholder.markdown("""
        <div class="owl-thinking">
            <span class="spin-owl">🦉</span>
            <p>Searching FAU policies...</p>
        </div>
        """, unsafe_allow_html=True)

        answer, sources = get_answer(question)
        placeholder.empty()

        st.markdown(answer)
        if sources:
            badges = "".join(
                f'<span class="source-badge">📄 {s.replace(".txt","").replace(".pdf","").replace("_"," ")}</span>'
                for s in sources
            )
            st.markdown(f"**Sources:** {badges}", unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })

    # Scroll to bottom after answer
    components.html("""
    <script>
        window.parent.document.querySelector('section.main').scrollTo({
            top: window.parent.document.querySelector('section.main').scrollHeight,
            behavior: 'smooth'
        });
    </script>
    """, height=0)
