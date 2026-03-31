"""
TruthSeeker — Streamlit Frontend
=================================
A premium fact-checking interface powered by the CRAG pipeline.

Usage:
    streamlit run app.py
"""

import streamlit as st
from graph import build_graph

# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG & CUSTOM CSS
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="TruthSeeker — AI Fact Checker",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Global ── */
    * { font-family: 'Inter', sans-serif; }
    .stApp {
        background: linear-gradient(160deg, #0a0a1a 0%, #111133 40%, #0d1b2a 100%);
    }

    /* ── Header ── */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00d2ff 0%, #7b2ff7 50%, #ff6b6b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0;
        letter-spacing: -1px;
        line-height: 1.1;
    }
    .hero-subtitle {
        text-align: center;
        color: #8892b0;
        font-size: 1.05rem;
        font-weight: 400;
        margin-top: 8px;
        margin-bottom: 35px;
    }
    .hero-badge {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 10px;
    }
    .badge {
        background: rgba(123, 47, 247, 0.15);
        border: 1px solid rgba(123, 47, 247, 0.3);
        color: #b8a9e8;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    /* ── Input area ── */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        color: #e6e6e6 !important;
        font-size: 1.05rem !important;
        padding: 18px !important;
        transition: all 0.3s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: rgba(123, 47, 247, 0.6) !important;
        box-shadow: 0 0 20px rgba(123, 47, 247, 0.15) !important;
    }
    .stTextArea label {
        color: #ccd6f6 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* ── Button ── */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #7b2ff7 0%, #4a90d9 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px 28px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(123, 47, 247, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(123, 47, 247, 0.45) !important;
    }

    /* ── Verdict Cards ── */
    .verdict-card {
        border-radius: 20px;
        padding: 30px;
        margin: 25px 0;
        backdrop-filter: blur(10px);
        animation: fadeInUp 0.6s ease-out;
    }
    .verdict-true {
        background: linear-gradient(135deg, rgba(0, 210, 106, 0.12) 0%, rgba(0, 180, 90, 0.06) 100%);
        border: 1px solid rgba(0, 210, 106, 0.3);
    }
    .verdict-false {
        background: linear-gradient(135deg, rgba(255, 82, 82, 0.12) 0%, rgba(220, 50, 50, 0.06) 100%);
        border: 1px solid rgba(255, 82, 82, 0.3);
    }
    .verdict-unverifiable {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.12) 0%, rgba(200, 150, 0, 0.06) 100%);
        border: 1px solid rgba(255, 193, 7, 0.3);
    }
    .verdict-label {
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .verdict-true .verdict-label { color: #00d26a; }
    .verdict-false .verdict-label { color: #ff5252; }
    .verdict-unverifiable .verdict-label { color: #ffc107; }

    .verdict-text {
        font-size: 2.2rem;
        font-weight: 900;
        margin-bottom: 4px;
    }
    .verdict-true .verdict-text { color: #00d26a; }
    .verdict-false .verdict-text { color: #ff5252; }
    .verdict-unverifiable .verdict-text { color: #ffc107; }

    .stance-badge {
        display: inline-block;
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 6px;
    }
    .stance-support {
        background: rgba(0, 210, 106, 0.15);
        color: #00d26a;
        border: 1px solid rgba(0, 210, 106, 0.3);
    }
    .stance-refute {
        background: rgba(255, 82, 82, 0.15);
        color: #ff5252;
        border: 1px solid rgba(255, 82, 82, 0.3);
    }
    .stance-neutral {
        background: rgba(255, 193, 7, 0.15);
        color: #ffc107;
        border: 1px solid rgba(255, 193, 7, 0.3);
    }

    /* ── Reasoning ── */
    .reasoning-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
        color: #b0bec5;
        font-size: 1rem;
        line-height: 1.7;
    }
    .reasoning-box h4 {
        color: #ccd6f6;
        margin-top: 0;
        margin-bottom: 12px;
        font-size: 1rem;
        font-weight: 700;
    }

    /* ── Route Log ── */
    .route-step {
        background: rgba(255, 255, 255, 0.03);
        border-left: 3px solid rgba(123, 47, 247, 0.5);
        padding: 10px 16px;
        margin: 6px 0;
        border-radius: 0 10px 10px 0;
        color: #8892b0;
        font-size: 0.9rem;
        font-family: 'Inter', monospace;
    }

    /* ── Source cards ── */
    .source-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        color: #8892b0;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .source-card strong {
        color: #ccd6f6;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        color: #ccd6f6 !important;
        font-weight: 600 !important;
    }

    /* ── Divider ── */
    .section-divider {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(123, 47, 247, 0.3), transparent);
        margin: 30px 0;
    }

    /* ── Animation ── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        color: #4a5568;
        font-size: 0.8rem;
        margin-top: 60px;
        padding: 20px;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def parse_verdict(generation: str) -> dict:
    """Parse the LLM's structured response into components."""
    result = {
        "verdict": "UNVERIFIABLE",
        "stance": "NEUTRAL",
        "reasoning": generation,
    }

    lines = generation.strip().split("\n")
    reasoning_lines = []
    capture_reasoning = False

    for line in lines:
        line_stripped = line.strip()
        if line_stripped.upper().startswith("VERDICT:"):
            verdict_text = line_stripped.split(":", 1)[1].strip().upper()
            if "TRUE" in verdict_text and "FALSE" not in verdict_text:
                result["verdict"] = "TRUE"
            elif "FALSE" in verdict_text:
                result["verdict"] = "FALSE"
            else:
                result["verdict"] = "UNVERIFIABLE"
        elif line_stripped.upper().startswith("STANCE:"):
            stance_text = line_stripped.split(":", 1)[1].strip().upper()
            if "SUPPORT" in stance_text:
                result["stance"] = "SUPPORT"
            elif "REFUTE" in stance_text:
                result["stance"] = "REFUTE"
            else:
                result["stance"] = "NEUTRAL"
        elif line_stripped.upper().startswith("REASONING:"):
            reasoning_lines.append(line_stripped.split(":", 1)[1].strip())
            capture_reasoning = True
        elif capture_reasoning:
            reasoning_lines.append(line_stripped)

    if reasoning_lines:
        result["reasoning"] = " ".join(reasoning_lines).strip()

    return result


def get_verdict_class(verdict: str) -> str:
    """Map verdict to CSS class."""
    mapping = {"TRUE": "verdict-true", "FALSE": "verdict-false"}
    return mapping.get(verdict, "verdict-unverifiable")


def get_stance_class(stance: str) -> str:
    """Map stance to CSS class."""
    mapping = {"SUPPORT": "stance-support", "REFUTE": "stance-refute"}
    return mapping.get(stance, "stance-neutral")


def get_verdict_icon(verdict: str) -> str:
    mapping = {"TRUE": "✅", "FALSE": "❌"}
    return mapping.get(verdict, "⚠️")


# ══════════════════════════════════════════════════════════════════
# LOAD GRAPH (cached)
# ══════════════════════════════════════════════════════════════════

@st.cache_resource
def load_graph():
    """Build and cache the LangGraph CRAG pipeline."""
    return build_graph()


# ══════════════════════════════════════════════════════════════════
# UI LAYOUT
# ══════════════════════════════════════════════════════════════════

# ── Hero Header ──
st.markdown("""
<div class="hero-badge">
    <span class="badge">CRAG PIPELINE</span>
    <span class="badge">GEMINI 2.0</span>
    <span class="badge">REAL-TIME</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<h1 class="hero-title">TruthSeeker</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">AI-powered fact-checking with Corrective RAG — verify any claim against '
    '21,000+ trusted news articles and live web evidence.</p>',
    unsafe_allow_html=True,
)

# ── Input Section ──
claim = st.text_area(
    "Enter a claim to fact-check",
    placeholder="e.g., \"NASA confirmed the discovery of water on Mars in 2018\"",
    height=100,
    key="claim_input",
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submit = st.button("🔍  Investigate Claim", use_container_width=True, key="submit_btn")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── Process Claim ──
if submit and claim.strip():
    graph = load_graph()

    with st.spinner("🔎 TruthSeeker is analyzing your claim..."):
        try:
            result = graph.invoke({
                "claim": claim.strip(),
                "documents": [],
                "web_search_needed": "no",
                "source_type": "database",
                "generation": "",
                "route_log": [],
            })

            # Parse the verdict
            parsed = parse_verdict(result.get("generation", ""))
            verdict = parsed["verdict"]
            stance = parsed["stance"]
            reasoning = parsed["reasoning"]
            verdict_class = get_verdict_class(verdict)
            stance_class = get_stance_class(stance)
            verdict_icon = get_verdict_icon(verdict)

            # ── Verdict Card ──
            st.markdown(f"""
            <div class="verdict-card {verdict_class}">
                <div class="verdict-label">VERDICT</div>
                <div class="verdict-text">{verdict_icon} {verdict}</div>
                <span class="stance-badge {stance_class}">Stance: {stance}</span>
            </div>
            """, unsafe_allow_html=True)

            # ── Reasoning ──
            st.markdown(f"""
            <div class="reasoning-box">
                <h4>💡 Reasoning</h4>
                {reasoning}
            </div>
            """, unsafe_allow_html=True)

            # ── Source Evidence ──
            documents = result.get("documents", [])
            source_type = result.get("source_type", "unknown")

            with st.expander(f"📄 Source Evidence — {len(documents)} documents ({source_type})", expanded=False):
                if documents:
                    for i, doc in enumerate(documents):
                        meta = doc.metadata
                        source_label = meta.get("source", meta.get("title", f"Document {i+1}"))
                        similarity = meta.get("similarity", meta.get("score", "N/A"))
                        if isinstance(similarity, float):
                            similarity = f"{similarity:.3f}"

                        st.markdown(f"""
                        <div class="source-card">
                            <strong>📌 {source_label}</strong><br>
                            <em style="color: #6c7a89;">Relevance Score: {similarity}</em>
                            <hr style="border-color: rgba(255,255,255,0.05); margin: 8px 0;">
                            {doc.page_content[:500]}{'...' if len(doc.page_content) > 500 else ''}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No source documents were used for this verdict.")

            # ── Routing Log ──
            route_log = result.get("route_log", [])
            with st.expander("🗺️ Agent Routing Path", expanded=False):
                if route_log:
                    for step in route_log:
                        st.markdown(
                            f'<div class="route-step">{step}</div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No routing data available.")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Make sure all API keys in `.env` are valid and the Supabase database is populated.")

elif submit:
    st.warning("⚠️ Please enter a claim before submitting.")

# ── Footer ──
st.markdown("""
<div class="footer">
    <p>TruthSeeker v1.0 — Corrective RAG Fact-Checking System</p>
    <p>Built with LangGraph · Gemini · Supabase · Tavily</p>
</div>
""", unsafe_allow_html=True)
