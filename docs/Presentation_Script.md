# TruthSeeker — Presentation & Demo Script

> **Format:** Screen-recorded presentation (NO SLIDES)  
> **Total Duration:** ~15–18 minutes  
> **Part 1 — Hassan:** Intro, Problem Statement, Live Demo, Dataset & Data Ingestion Code (~7–9 min)  
> **Part 2 — Haad:** Architecture, Graph Code Walkthrough & Conclusion (~7–9 min)

---

## Setup Before Recording

- Have the Streamlit app **already running** in the background (`streamlit run src/app.py`).
- Have VS Code open with `src/ingest.py`, `src/graph.py`, and `src/app.py` tabs ready.
- **Start the recording on the browser with the Streamlit app open.**
- Speak slowly and clearly. Pause after key points.

---

---

# 🟦 PART 1 — HASSAN

## 1. Introduction & The Problem (Keep Streamlit App on screen)

**[Start recording with the Streamlit app visible in the browser]**

> *"Good morning/afternoon, Dr. Mangrio and class. Our project is called **TruthSeeker** — an AI-powered fact-checking system built using a Corrective Retrieval-Augmented Generation pipeline, or CRAG for short."*
>
> *"I'm Hassan, CMS ID 023-23-0200, and my teammate is Haad, CMS ID 023-23-0199. This is our semester project for the Introduction to Artificial Intelligence course."*
>
> *"Before we show you the code, let's talk about why we built this. We all know how fast misinformation travels. Large Language Models like ChatGPT can answer questions, but they have a critical flaw — **hallucination**. They confidently make up facts."*
>
> *"Standard RAG tries to fix this by searching a database first, but it blindly trusts whatever it finds. If it pulls bad documents, the LLM hallucinates anyway. **TruthSeeker solves this** by adding a correction step. It evaluates its own evidence, and if the evidence is bad, it falls back to a live web search from trusted sources."*

---

## 2. Live Demo (Still on the Streamlit App)

> *"Let me show you exactly what I mean using this interface we built."*

### Demo 1: In-Database Claim (TRUE)

**[Type in the text box: `Donald Trump signed an executive order regarding immigration in early 2017`]**  
**[Click "Investigate Claim"]**

> *"I'm entering a claim about Trump signing an immigration executive order in 2017. This is well within our dataset's coverage."*

**[Wait for result]**

> *"The verdict is **TRUE**, stance is **SUPPORT**. If I expand the routing path below, you can see our agent's thought process: It RETRIEVED 5 documents, GRADED them, found them relevant, and went **directly to GENERATE**, completely skipping the web search."*

**[Expand "Source Evidence" section]**

> *"And here you can see the actual database documents it used."*

### Demo 2: Out-of-Distribution Claim (Web Fallback)

**[Type: `The 2022 FIFA World Cup was held in Qatar`]**  
**[Click "Investigate Claim"]**

> *"Now let's test something our database has **no information about** — the 2022 World Cup. Our dataset only goes up to 2017."*

**[Wait for result]**

> *"Look at the routing path now. It pulled 5 documents, but the Grader found **0 out of 5 relevant**. So it triggered the **WEB SEARCH** fallback, searched trusted sources like Reuters and AP News, and then generated a **TRUE** verdict."*
>
> *"This is the Corrective RAG in action — the agent recognized its own knowledge gap and adapted."*

### Demo 3: Common Myth (FALSE)

**[Type: `Humans only use 10% of their brain`]**  
**[Click "Investigate Claim"]**

> *"Let's test a popular myth."*

**[Wait for result]**

> *"Verdict: **FALSE**, Stance: **REFUTE**. Again, it went to web search, found fact-checking sources that debunk this myth, and correctly identified it as false."*

---

## 3. Dataset & Pre-processing (Switch to VS Code)

**[Switch screen to VS Code and open `src/ingest.py`]**

> *"So how does the local knowledge base work? We use the **Fake and Real News Dataset** from Kaggle, specifically the 21,417 verified, factual news articles from Reuters."*
>
> *"Raw articles can't be searched semantically. We process them here in `ingest.py`."*

**[Scroll to line 70 — `chunk_documents`]**

> *"At line 70, we use a RecursiveCharacterTextSplitter to break the articles into 500-character chunks with a 50-character overlap. This expands our 21,000 articles into over **130,000 searchable chunks**."*

**[Scroll to line 96 — `generate_embeddings`]**

> *"At line 96, we use the `all-MiniLM-L6-v2` model to convert each chunk into a 384-dimensional vector."*

**[Scroll to line 109 — `insert_into_supabase`]**

> *"Finally, we batch insert these 130,000 vectors into a **Supabase PostgreSQL database**. We use an IVFFlat index — which clusters the vectors so search is almost instant."*

---

> **HASSAN's TRANSITION:**  
> *"So that covers the data foundation and the interface. Now Haad will walk you through **how the brain actually thinks** — the CRAG pipeline architecture and the LangGraph code behind it."*

---

---

# 🟧 PART 2 — HAAD

## 4. Architecture Overview (Stay in VS Code, open `src/graph.py`)

> *"Thanks, Hassan. Let me explain the brain of TruthSeeker."*
>
> *"The core of our system is a **4-node state machine** built using **LangGraph**. Unlike a standard linear script, LangGraph lets us define our agent as a directed graph where each node reads from and writes to a shared state."*

**[Scroll to line 64 — `GraphState` class]**

> *"Here at line 64 is our state definition. Every node in the graph reads and writes to this object. You can see the `route_log` list here — this is what powers the transparent decision trail Hassan just showed in the UI."*

### Node 1: Retrieve

**[Scroll to line 78 — `retrieve` function]**

> *"Line 78 is Node 1: **Retrieve**. It takes the user's claim, converts it to a vector, and runs a cosine similarity search against Supabase. Cosine similarity measures the semantic angle between vectors, ignoring text length. It retrieves the top 5 most similar chunks."*

### Node 2: Grade Documents

**[Scroll to line 143 — `grade_documents` function]**

> *"Line 143 is Node 2: **Grade**. This is the core innovation. We pass the 5 documents to **Llama 3.3 70B** and ask: 'Are these actually relevant?' Look at the prompt on line 125 — we force the LLM to output only the IDs of relevant documents."*
> *"At line 180, if fewer than 2 documents are relevant, we set an internal flag: `web_search_needed = yes`."*

### Node 3: Web Search (Conditional)

**[Scroll to line 200 — `web_search` function]**

> *"Line 200 is Node 3: **Web Search**. Notice on line 215 the `include_domains` parameter. If the grading failed, we search the live internet using Tavily, but we constrain it to trusted domains only: Reuters, AP News, Snopes, FactCheck.org. We don't search the wild web."*

### Node 4: Generate Verdict

**[Scroll to line 302 — `generate` function]**

> *"Line 302 is Node 4: **Generate**. The LLM performs stance detection based on the evidence. A key detail is on line 326 — we dynamically inject the **current system date** into the prompt. This allows TruthSeeker to handle time-relative claims correctly."*

**[Scroll to line 357 — `build_graph` function]**

> *"Line 357 is `build_graph` where it all connects. We add the four nodes, and the **conditional edge** at line 380 routes from Grading to either Web Search or directly to Generate."*

---

## 5. Fault Tolerance & UI Code (Briefly show `src/app.py`)

**[Scroll to line 44 in `graph.py` — `invoke_with_retry`]**

> *"I also want to point out line 44: `invoke_with_retry`. API limits are a real problem. We implemented an exponential backoff algorithm. If the Groq API throws a Rate Limit error, our agent gracefully pauses for 15 seconds and retries instead of crashing."*

**[Switch to `src/app.py` in VS Code]**

> *"And briefly on the frontend, this is `app.py`. We used Streamlit with fully custom CSS starting at line 24 to create the premium dark mode, the dynamic verdict cards, and the expander sections."*

---

## 6. Conclusion (Stay on screen or switch back to the App)

> *"To summarize what TruthSeeker brings together from our AI course:"*
>
> *"**Intelligent Agents** — our system is modeled as a goal-based rational agent with sensors, actuators, and an internal state."*
>
> *"**Search Strategies** — the vector search uses cosine similarity as a heuristic function, acting as an informed search strategy."*
>
> *"**Handling Uncertainty** — the UNVERIFIABLE class and the grading mechanism are direct applications of acting under uncertainty."*
>
> *"And **Machine Learning** — from text embeddings for feature extraction, to document classification in the grading node, to web search for handling out-of-distribution generalization."*
>
> *"Thank you. We're happy to take any questions."*

---

## 🛑 Backup: Anticipated Q&A

| Question | Answer |
|----------|--------|
| **Why not fine-tune your own model?** | Fine-tuning requires massive labeled fact-checking datasets and GPU compute. Using pre-trained models (MiniLM for embedding, Llama 3.3 for reasoning) with carefully engineered prompts achieves strong results without that overhead. |
| **Why cosine similarity over other distance metrics?** | Cosine ignores vector magnitude and focuses on direction (semantic angle). Text length varies wildly, so Euclidean distance would be biased by article length. Cosine is magnitude-invariant. |
| **What if the web search also fails?** | The system has error handling — if Tavily fails, it falls back to whatever database docs it had. In the worst case, it generates with "no evidence found" and will likely return UNVERIFIABLE. |
| **Why the 2-document threshold for web search?** | Having just 1 relevant doc is weak evidence. 2 is the minimum for cross-referencing. If the database returns 5 but only 1 is relevant, that's a strong signal the database lacks coverage. |
| **Why Groq instead of running Llama locally?** | Groq's LPU hardware generates tokens ~10x faster than GPU inference. For an interactive demo, speed matters. |
