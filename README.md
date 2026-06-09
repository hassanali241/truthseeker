# 🔍 TruthSeeker

**AI-Powered Fact-Checking with Corrective RAG (CRAG)**

TruthSeeker is a 4-node LangGraph pipeline that retrieves evidence, self-grades relevance, searches the live web when needed, and delivers structured **TRUE / FALSE / UNVERIFIABLE** verdicts.

Built with **Python · LangGraph · Groq (Llama 3.3 70B) · Supabase · Tavily · Streamlit**

---

## 📁 Project Structure

```
TruthSeeker/
├── src/                    # Core source code
│   ├── app.py              # Streamlit frontend UI
│   ├── graph.py            # CRAG pipeline (LangGraph state machine)
│   ├── ingest.py           # Data ingestion → Supabase
│   └── config.py           # Shared secrets & config loader
│
├── scripts/                # Utility scripts
│   ├── generate_pdf.py     # LinkedIn PDF generator (ReportLab)
│   └── generate_beautiful_pdf.py  # Beautiful PDF generator (Playwright)
│
├── db/                     # Database setup
│   └── supabase_setup.sql  # pgvector table & function setup
│
├── tests/                  # Test scripts
│   └── test_graph.py       # Quick graph smoke test
│
├── data/                   # Dataset (not in git)
│   └── True.csv            # 21,000+ verified news articles
│
├── assets/                 # Images & screenshots
│   ├── Interface.png
│   ├── Evidence-Backed.png
│   └── Log.png
│
├── docs/                   # Documentation & generated PDFs
│   ├── TruthSeeker_Flow.pdf
│   ├── TruthSeeker_Walkthrough.pdf
│   └── ...
│
├── .env                    # API keys (not in git)
├── .gitignore
├── .streamlit/             # Streamlit Cloud config
│   └── secrets.toml.example
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

### Prerequisites
- Python 3.9+
- Supabase account
- Groq API key
- Tavily API key

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
#    Create a .env file in the project root with:
#    SUPABASE_URL, SUPABASE_KEY, GROQ_API_KEY, TAVILY_API_KEY

# 3. Set up the vector database (one-time)
#    Run db/supabase_setup.sql in your Supabase SQL Editor

# 4. Ingest the fact-check dataset (~10-20 min)
python src/ingest.py

# 5. Launch the web app
streamlit run src/app.py
```

---

## ⚙️ Architecture

```
Claim → RETRIEVE → GRADE DOCUMENTS → [relevant?] → GENERATE → Verdict
                                    → [not relevant?] → WEB SEARCH → GENERATE → Verdict
```

| Node | Description |
|------|-------------|
| **Retrieve** | Cosine similarity search via Supabase pgvector |
| **Grade Documents** | LLM filters irrelevant docs from results |
| **Web Search** | Tavily API fallback (Reuters, BBC, Snopes, etc.) |
| **Generate** | Produces VERDICT + STANCE + REASONING |

---

## 🛠 Tech Stack

| Library | Role |
|---------|------|
| LangGraph | State machine / graph execution engine |
| Groq (Llama 3.3 70B) | LLM for grading, stance detection, verdict generation |
| Supabase + pgvector | Vector database for embedded documents |
| Sentence-Transformers | all-MiniLM-L6-v2 — 384-dim embeddings |
| Tavily API | Real-time web search (trusted domains only) |
| Streamlit | Frontend web UI |

---

## 👤 Author

**Hassan Ali** — AI Engineer  
[GitHub](https://github.com/hassanali241) · [LinkedIn](https://www.linkedin.com/in/hassan-ali-46a58b28a/)
