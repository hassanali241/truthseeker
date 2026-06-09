from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import KeepTogether

# ── Colors ──────────────────────────────────────────────────────────
DARK_BG    = colors.HexColor("#0a0a1a")
CYAN       = colors.HexColor("#00d4ff")
PURPLE     = colors.HexColor("#7c3aed")
GREEN      = colors.HexColor("#10b981")
RED        = colors.HexColor("#ef4444")
YELLOW     = colors.HexColor("#f59e0b")
LIGHT_GRAY = colors.HexColor("#e2e8f0")
MID_GRAY   = colors.HexColor("#94a3b8")
CARD_BG    = colors.HexColor("#1e1e3a")
WHITE      = colors.white

W, H = A4

doc = SimpleDocTemplate(
    "docs/TruthSeeker_LinkedIn.pdf",
    pagesize=A4,
    rightMargin=1.5*cm, leftMargin=1.5*cm,
    topMargin=1.5*cm, bottomMargin=1.5*cm
)

styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

title_style   = S("Title",   fontSize=32, textColor=CYAN,     alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=8)
sub_style     = S("Sub",     fontSize=16, textColor=LIGHT_GRAY, alignment=TA_CENTER, fontName="Helvetica",    spaceAfter=6)
tag_style     = S("Tag",     fontSize=11, textColor=MID_GRAY,  alignment=TA_CENTER, fontName="Helvetica",    spaceAfter=4)
h2_style      = S("H2",      fontSize=20, textColor=CYAN,     fontName="Helvetica-Bold", spaceAfter=10)
h3_style      = S("H3",      fontSize=14, textColor=PURPLE,   fontName="Helvetica-Bold", spaceAfter=6)
body_style    = S("Body",    fontSize=11, textColor=LIGHT_GRAY, fontName="Helvetica", leading=16, spaceAfter=6)
bullet_style  = S("Bullet",  fontSize=11, textColor=LIGHT_GRAY, fontName="Helvetica", leading=18, leftIndent=20, spaceAfter=4, bulletIndent=8)
code_style    = S("Code",    fontSize=9,  textColor=CYAN,     fontName="Courier",   leading=14, leftIndent=10, spaceAfter=4, backColor=CARD_BG)
label_style   = S("Label",   fontSize=10, textColor=MID_GRAY, fontName="Helvetica-Oblique", spaceAfter=2)
center_body   = S("CBody",   fontSize=11, textColor=LIGHT_GRAY, fontName="Helvetica", leading=16, alignment=TA_CENTER, spaceAfter=6)

def rule():
    return HRFlowable(width="100%", thickness=1, color=PURPLE, spaceAfter=12, spaceBefore=4)

def sp(n=8):
    return Spacer(1, n)

def colored_table(rows, col_widths, bg=CARD_BG, header_bg=PURPLE):
    t = Table(rows, colWidths=col_widths)
    style = [
        ("BACKGROUND", (0,0), (-1,0), header_bg),
        ("BACKGROUND", (0,1), (-1,-1), bg),
        ("TEXTCOLOR",  (0,0), (-1,0), WHITE),
        ("TEXTCOLOR",  (0,1), (-1,-1), LIGHT_GRAY),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",   (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",   (0,0), (-1,-1), 10),
        ("ALIGN",      (0,0), (-1,-1), "LEFT"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#2d2d5a")),
        ("ROWBACKGROUND", (0,1), (-1,-1), [CARD_BG, colors.HexColor("#16163a")]),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
    ]
    t.setStyle(TableStyle(style))
    return t

def node_box(num, title, color, lines):
    header = [[Paragraph(f"<b>Node {num}: {title}</b>", S("nh", fontSize=12, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER))]]
    ht = Table(header, colWidths=[W - 3*cm])
    ht.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), color),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    body_rows = [[Paragraph(f"• {l}", body_style)] for l in lines]
    bt = Table(body_rows, colWidths=[W - 3*cm])
    bt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CARD_BG),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#2d2d5a")),
    ]))
    return [ht, bt, sp(10)]

story = []

# ═══════════════════════════════════════════════════════════════════
# PAGE 1 — COVER
# ═══════════════════════════════════════════════════════════════════
story += [
    sp(60),
    Paragraph("🔍 TruthSeeker", title_style),
    sp(6),
    Paragraph("AI-Powered Fact-Checking with Corrective RAG", sub_style),
    sp(20),
    rule(),
    sp(10),
    Paragraph("A 4-node LangGraph CRAG pipeline that retrieves evidence,<br/>"
              "self-grades relevance, searches the live web when needed,<br/>"
              "and delivers a structured TRUE / FALSE / UNVERIFIABLE verdict.", center_body),
    sp(20),
    Paragraph("Python  ·  LangGraph  ·  Groq (Llama 3.3 70B)  ·  Supabase  ·  Tavily  ·  Streamlit", tag_style),
    sp(60),
    Paragraph("Hassan Ali  —  AI Engineer", S("Footer", fontSize=10, textColor=MID_GRAY, alignment=TA_CENTER, fontName="Helvetica-Oblique")),
    PageBreak(),
]

# ═══════════════════════════════════════════════════════════════════
# PAGE 2 — THE PROBLEM
# ═══════════════════════════════════════════════════════════════════
story += [
    Paragraph("The Problem", h2_style),
    rule(),
    sp(6),
    Paragraph("Misinformation spreads faster than corrections. Standard LLMs hallucinate. "
              "Standard RAG blindly trusts whatever it retrieves — relevant or not.", body_style),
    sp(10),
    Paragraph("TruthSeeker fixes this with <b>Corrective RAG (CRAG)</b>:", body_style),
    sp(8),
    colored_table(
        [
            [Paragraph("<b>Standard RAG</b>", S("th", fontSize=11, textColor=WHITE, fontName="Helvetica-Bold")),
             Paragraph("<b>TruthSeeker CRAG</b>", S("th", fontSize=11, textColor=WHITE, fontName="Helvetica-Bold"))],
            [Paragraph("Retrieves docs blindly", body_style),        Paragraph("Grades retrieved docs for relevance", body_style)],
            [Paragraph("Uses irrelevant evidence",  body_style),      Paragraph("Filters out noise automatically", body_style)],
            [Paragraph("No fallback if DB fails",   body_style),      Paragraph("Falls back to live web search", body_style)],
            [Paragraph("No source transparency",    body_style),      Paragraph("Full audit log of every step", body_style)],
            [Paragraph("Hallucination-prone",       body_style),      Paragraph("Evidence-grounded verdicts", body_style)],
        ],
        [(W-3*cm)/2, (W-3*cm)/2]
    ),
    PageBreak(),
]

# ═══════════════════════════════════════════════════════════════════
# PAGE 3 — ARCHITECTURE OVERVIEW
# ═══════════════════════════════════════════════════════════════════
story += [
    Paragraph("Architecture Overview", h2_style),
    rule(),
    sp(8),
    Paragraph("The pipeline is a <b>LangGraph StateGraph</b> — a directed graph where each node "
              "reads from and writes to a shared GraphState object.", body_style),
    sp(12),
]

flow_rows = [
    [Paragraph("<b>Step</b>", S("th", fontSize=11, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("<b>Node</b>", S("th", fontSize=11, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("<b>What Happens</b>", S("th", fontSize=11, textColor=WHITE, fontName="Helvetica-Bold"))],
    [Paragraph("1", body_style), Paragraph("Retrieve", body_style),        Paragraph("Embed the claim → cosine search in Supabase vector DB", body_style)],
    [Paragraph("2", body_style), Paragraph("Grade Documents", body_style), Paragraph("LLM checks: are retrieved docs actually relevant?", body_style)],
    [Paragraph("3*", body_style), Paragraph("Web Search", body_style),     Paragraph("If <2 relevant docs → search Reuters, BBC, Snopes via Tavily", body_style)],
    [Paragraph("4", body_style), Paragraph("Generate", body_style),        Paragraph("Produce VERDICT + STANCE + REASONING from evidence", body_style)],
]

story += [
    colored_table(flow_rows, [1.5*cm, 4*cm, W-3*cm-1.5*cm-4*cm]),
    sp(12),
    Paragraph("* Step 3 is conditional — only triggered when the knowledge base lacks sufficient evidence.", label_style),
    sp(10),
    Paragraph("Flow:", h3_style),
    Paragraph(
        "Claim → <b>Retrieve</b> → <b>Grade</b> → [relevant? → <b>Generate</b>] [not relevant? → <b>Web Search</b> → <b>Generate</b>] → Verdict",
        S("flow", fontSize=11, textColor=CYAN, fontName="Courier", leading=18, alignment=TA_CENTER)
    ),
    PageBreak(),
]

# ═══════════════════════════════════════════════════════════════════
# PAGE 4 — THE 4 NODES
# ═══════════════════════════════════════════════════════════════════
story += [
    Paragraph("The 4 Nodes — Deep Dive", h2_style),
    rule(),
    sp(6),
]
story += node_box(1, "Retrieve", colors.HexColor("#0e7490"), [
    "Encodes the user's claim into a 384-dim vector using all-MiniLM-L6-v2",
    "Calls Supabase match_documents() RPC — cosine similarity search",
    "Returns top-5 most similar documents from the knowledge base",
])
story += node_box(2, "Grade Documents", PURPLE, [
    "Sends all 5 docs to Llama 3.3 70B in a single batch prompt",
    "LLM returns IDs of relevant documents (e.g. '0, 2, 4') or 'NONE'",
    "If fewer than 2 relevant docs found → sets web_search_needed = 'yes'",
])
story += node_box(3, "Web Search (Fallback)", colors.HexColor("#b45309"), [
    "Only activated when DB evidence is insufficient",
    "Queries Tavily with trusted domains only: Reuters, BBC, AP News, Snopes, FactCheck.org",
    "Merges web results with any existing DB docs (source_type = 'both')",
])
story += node_box(4, "Generate Verdict", colors.HexColor("#065f46"), [
    "Receives all evidence documents + current system date",
    "LLM produces structured output: VERDICT / STANCE / REASONING",
    "Verdicts: TRUE · FALSE · UNVERIFIABLE  |  Stances: SUPPORT · REFUTE · NEUTRAL",
])
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════
# PAGE 5 — TECH STACK
# ═══════════════════════════════════════════════════════════════════
story += [
    Paragraph("Tech Stack", h2_style),
    rule(),
    sp(8),
    colored_table(
        [
            [Paragraph("<b>Library</b>", S("th", fontSize=11, textColor=WHITE, fontName="Helvetica-Bold")),
             Paragraph("<b>Role</b>", S("th", fontSize=11, textColor=WHITE, fontName="Helvetica-Bold"))],
            [Paragraph("LangGraph", body_style),            Paragraph("State machine / graph execution engine", body_style)],
            [Paragraph("LangChain / langchain-core", body_style), Paragraph("Prompt templates, document objects, output parsers", body_style)],
            [Paragraph("Groq API — Llama 3.3 70B", body_style), Paragraph("LLM for grading, stance detection, verdict generation", body_style)],
            [Paragraph("Supabase + pgvector", body_style),  Paragraph("Vector database — stores and retrieves embedded documents", body_style)],
            [Paragraph("Sentence-Transformers", body_style), Paragraph("all-MiniLM-L6-v2 — converts text to 384-dim embeddings", body_style)],
            [Paragraph("Tavily API", body_style),           Paragraph("Real-time web search restricted to trusted fact-check domains", body_style)],
            [Paragraph("Streamlit", body_style),            Paragraph("Frontend web UI — dark-themed, animated verdict cards", body_style)],
            [Paragraph("Pandas", body_style),               Paragraph("Loading and processing the CSV fact-check dataset", body_style)],
        ],
        [4.5*cm, W-3*cm-4.5*cm]
    ),
    PageBreak(),
]

# ═══════════════════════════════════════════════════════════════════
# PAGE 6 — SAMPLE VERDICTS
# ═══════════════════════════════════════════════════════════════════
story += [
    Paragraph("Sample Verdicts", h2_style),
    rule(),
    sp(8),
]

def verdict_box(claim, verdict, stance, reasoning, v_color):
    rows = [
        [Paragraph(f"<b>Claim:</b> {claim}", body_style)],
        [Paragraph(f"<b>Verdict:</b> {verdict}  |  <b>Stance:</b> {stance}", S("vd", fontSize=12, textColor=v_color, fontName="Helvetica-Bold"))],
        [Paragraph(f"<b>Reasoning:</b> {reasoning}", body_style)],
    ]
    t = Table(rows, colWidths=[W-3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CARD_BG),
        ("LINEAFTER",  (0,0), (0,-1), 4, v_color),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#2d2d5a")),
    ]))
    return [t, sp(10)]

story += verdict_box(
    "Humans only use 10% of their brain.",
    "FALSE", "REFUTE",
    "Neuroimaging studies consistently show that virtually all areas of the brain "
    "have some function and are active over the course of a day. The 10% myth is unsupported by neuroscience.",
    RED
)
story += verdict_box(
    "The Great Wall of China is visible from space.",
    "FALSE", "REFUTE",
    "NASA and astronauts including Chinese astronaut Yang Liwei have confirmed the wall is too narrow "
    "to be seen with the naked eye from low Earth orbit.",
    RED
)
story += verdict_box(
    "Nelson Mandela was imprisoned for 27 years.",
    "TRUE", "SUPPORT",
    "Nelson Mandela was incarcerated from 1964 to 1990 — a period of 27 years — primarily at Robben Island, "
    "Pollsmoor Prison, and Victor Verster Prison.",
    GREEN
)
story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════
# PAGE 7 — HOW TO RUN
# ═══════════════════════════════════════════════════════════════════
story += [
    Paragraph("How to Run", h2_style),
    rule(),
    sp(8),
    Paragraph("Prerequisites: Python 3.9+, a Supabase account, Groq API key, Tavily API key.", body_style),
    sp(10),
]

steps = [
    ("1. Install dependencies",    "pip install -r requirements.txt"),
    ("2. Configure API keys",      "Create a .env file with:\nSUPABASE_URL, SUPABASE_KEY, GROQ_API_KEY, TAVILY_API_KEY"),
    ("3. Set up vector database",  "Run db/supabase_setup.sql in your Supabase SQL editor (one-time)"),
    ("4. Ingest fact-check data",  "python src/ingest.py   # embeds CSV data into Supabase (~10–20 min)"),
    ("5. Launch the web app",      "streamlit run src/app.py"),
]

for label, cmd in steps:
    story.append(Paragraph(f"<b>{label}</b>", h3_style))
    story.append(Paragraph(cmd, code_style))
    story.append(sp(8))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════════════
# PAGE 8 — CLOSING / CTA
# ═══════════════════════════════════════════════════════════════════
story += [
    sp(50),
    Paragraph("Built by Hassan Ali", S("ct", fontSize=22, textColor=CYAN, fontName="Helvetica-Bold", alignment=TA_CENTER)),
    sp(8),
    Paragraph("AI Engineer  ·  Python  ·  LangGraph  ·  GenAI", tag_style),
    sp(20),
    rule(),
    sp(10),
    Paragraph("🔗  GitHub Repository", S("gh", fontSize=14, textColor=PURPLE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
    sp(6),
    Paragraph("github.com/hassanali241/truthseeker", S("url", fontSize=12, textColor=CYAN, fontName="Courier", alignment=TA_CENTER)),
    sp(20),
    Paragraph("What claim would you fact-check first? 👇", S("cta", fontSize=14, textColor=LIGHT_GRAY, fontName="Helvetica-Oblique", alignment=TA_CENTER)),
]

doc.build(story)
print("DONE: TruthSeeker_LinkedIn.pdf generated successfully!")
