"""
TruthSeeker — CRAG Brain (Corrective RAG)
==========================================
LangGraph state machine with 4 nodes:
  1. Retrieve  - cosine similarity search in Supabase
  2. Grade     - LLM evaluates document relevance
  3. Web Search - Tavily fallback for irrelevant results
  4. Generate  - Stance detection + verdict generation

Usage:
    from graph import build_graph
    graph = build_graph()
    result = graph.invoke({"claim": "Some claim to fact-check"})
"""

import os
import time
import datetime
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from tavily import TavilyClient

from langgraph.graph import StateGraph, END

# ── Load environment ───────────────────────────────────────────────
# Supports both local (.env file) and Streamlit Cloud (st.secrets)
load_dotenv()

def _get_secret(key: str) -> str:
    """Read from Streamlit secrets (cloud) or .env (local)."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)

SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_KEY")
GROQ_API_KEY = _get_secret("GROQ_API_KEY")
TAVILY_API_KEY = _get_secret("TAVILY_API_KEY")

# ── Initialize clients ────────────────────────────────────────────
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0,
)


def invoke_with_retry(chain, inputs, max_retries=3):
    """Invoke an LLM chain with automatic retry on rate limit (429) errors."""
    for attempt in range(max_retries):
        try:
            return chain.invoke(inputs)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = 15 * (attempt + 1)  # 15s, 30s, 45s
                print(f"   ⏳ Rate limited. Retrying in {wait_time}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise e
    return chain.invoke(inputs)  # Final attempt


# ══════════════════════════════════════════════════════════════════
# STATE DEFINITION
# ══════════════════════════════════════════════════════════════════

class GraphState(TypedDict):
    """State object passed between LangGraph nodes."""
    claim: str                       # The user's input claim
    documents: List[Document]        # Retrieved / web-searched docs
    web_search_needed: str           # "yes" | "no"
    source_type: str                 # "database" | "web" | "both"
    generation: str                  # Final verdict + reasoning
    route_log: List[str]             # Visual log of routing path


# ══════════════════════════════════════════════════════════════════
# NODE 1: RETRIEVE
# ══════════════════════════════════════════════════════════════════

def retrieve(state: GraphState) -> GraphState:
    """
    Embed the user's claim and perform cosine similarity search
    against the Supabase vector store.
    """
    claim = state["claim"]
    route_log = state.get("route_log", [])
    route_log.append("📥 Node: RETRIEVE — Searching knowledge base...")

    # Generate embedding for the claim
    claim_embedding = embedding_model.encode(claim).tolist()

    # Query Supabase for top-5 similar documents
    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": claim_embedding,
            "match_count": 5,
        },
    ).execute()

    documents = []
    if response.data:
        for doc in response.data:
            documents.append(
                Document(
                    page_content=doc["content"],
                    metadata={
                        **(doc.get("metadata") or {}),
                        "similarity": doc.get("similarity", 0),
                    },
                )
            )

    route_log.append(f"   ✅ Retrieved {len(documents)} documents from database")

    return {
        **state,
        "documents": documents,
        "route_log": route_log,
    }


# ══════════════════════════════════════════════════════════════════
# NODE 2: GRADE DOCUMENTS
# ══════════════════════════════════════════════════════════════════

GRADING_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a relevance grader. You assess which of the provided documents are relevant to fact-checking a user's claim.

Rules:
- A document is "relevant" if it contains information that could help verify or refute the claim.
- The documents are provided with IDs (e.g., "--- Document 0 ---").
- Respond with a comma-separated list of ONLY the IDs of relevant documents (e.g., "0, 2, 4").
- If NO documents are relevant, reply with exactly "NONE". Do not include any other text.""",
    ),
    (
        "human",
        "Claim: {claim}\n\nDocuments:\n{documents}\n\nRelevant Document IDs:",
    ),
])


def grade_documents(state: GraphState) -> GraphState:
    """
    LLM-based relevance grading. Checks all documents in a single batch call.
    If fewer than 2 documents are relevant, flags for web search fallback.
    """
    claim = state["claim"]
    documents = state["documents"]
    route_log = state.get("route_log", [])
    route_log.append(f"🔍 Node: GRADE — Evaluating relevance of {len(documents)} documents...")

    if not documents:
        return {
            **state,
            "web_search_needed": "yes",
            "route_log": route_log + ["   ⚠️ No documents to grade. Fallback to web search."],
        }

    docs_text = "\n\n".join(
        f"--- Document {i} ---\n{doc.page_content}"
        for i, doc in enumerate(documents)
    )

    grading_chain = GRADING_PROMPT | llm | StrOutputParser()
    grade_response = invoke_with_retry(grading_chain, {
        "claim": claim,
        "documents": docs_text,
    }).strip().upper()

    relevant_docs = []
    if grade_response != "NONE":
        # Extract numbers from response
        relevant_ids = [int(s) for s in grade_response.replace(",", " ").split() if s.isdigit()]
        for idx in relevant_ids:
            if 0 <= idx < len(documents):
                relevant_docs.append(documents[idx])

    # Decision: need web search if fewer than 2 relevant docs
    web_search_needed = "yes" if len(relevant_docs) < 2 else "no"

    route_log.append(
        f"   ✅ {len(relevant_docs)}/{len(documents)} docs graded relevant → "
        f"{'Web search needed' if web_search_needed == 'yes' else 'Sufficient evidence found'}"
    )

    return {
        **state,
        "documents": relevant_docs,
        "web_search_needed": web_search_needed,
        "source_type": "database" if web_search_needed == "no" else state.get("source_type", "database"),
        "route_log": route_log,
    }


# ══════════════════════════════════════════════════════════════════
# NODE 3: WEB SEARCH (Tavily)
# ══════════════════════════════════════════════════════════════════

def web_search(state: GraphState) -> GraphState:
    """
    Fallback: search the live web using Tavily API when the
    knowledge base doesn't have sufficient relevant documents.
    """
    claim = state["claim"]
    documents = state.get("documents", [])
    route_log = state.get("route_log", [])
    route_log.append("🌐 Node: WEB SEARCH — Querying live web via Tavily...")

    try:
        # Search with trusted domain hints
        search_results = tavily_client.search(
            query=f"fact check: {claim}",
            max_results=5,
            include_domains=[
                "reuters.com", "apnews.com", "bbc.com",
                "snopes.com", "factcheck.org", "politifact.com",
            ],
        )

        web_docs = []
        for result in search_results.get("results", []):
            web_docs.append(
                Document(
                    page_content=result.get("content", ""),
                    metadata={
                        "source": result.get("url", ""),
                        "title": result.get("title", ""),
                        "score": result.get("score", 0),
                        "source_type": "web",
                    },
                )
            )

        # Combine with any existing relevant docs from database
        all_docs = documents + web_docs
        source_type = "both" if documents else "web"

        route_log.append(f"   ✅ Found {len(web_docs)} web results")

    except Exception as e:
        route_log.append(f"   ❌ Web search failed: {str(e)}")
        all_docs = documents
        source_type = "database" if documents else "none"

    return {
        **state,
        "documents": all_docs,
        "source_type": source_type,
        "route_log": route_log,
    }


# ══════════════════════════════════════════════════════════════════
# NODE 4: GENERATE VERDICT
# ══════════════════════════════════════════════════════════════════

GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are TruthSeeker, an expert fact-checking AI. Your task is to analyze
evidence and determine whether a claim is TRUE, FALSE, or UNVERIFIABLE.

IMPORTANT RULE: You are given the CURRENT SYSTEM DATE at the start of each query.
This date is 100% accurate and authoritative. Use it directly to evaluate any
time-relative claims such as "today is Monday", "it is currently March", etc.
Do NOT mark these as UNVERIFIABLE — you have the date and CAN verify them.

Instructions:
1. For claims about the current day/date/month/year: use CURRENT SYSTEM DATE directly.
   Verify: does the claim match the system date? If yes → TRUE. If no → FALSE.
2. For all other factual claims: analyze the provided evidence documents.
3. Determine the STANCE of the evidence toward the claim:
   - SUPPORT: The evidence agrees with / confirms the claim.
   - REFUTE: The evidence contradicts / disproves the claim.
   - NEUTRAL: The evidence is insufficient or inconclusive.
4. Issue a verdict:
   - TRUE: Confirmed by system date OR majority of evidence supports the claim.
   - FALSE: Contradicts system date OR majority of evidence refutes the claim.
   - UNVERIFIABLE: ONLY if neither date NOR evidence can resolve the claim.
5. Provide a concise reasoning paragraph (2-4 sentences).

FORMAT YOUR RESPONSE EXACTLY AS:
VERDICT: [TRUE/FALSE/UNVERIFIABLE]
STANCE: [SUPPORT/REFUTE/NEUTRAL]
REASONING: [Your explanation paragraph]""",
    ),
    (
        "human",
        """[CURRENT SYSTEM DATE: {current_date}]

CLAIM: {claim}

EVIDENCE DOCUMENTS:
{evidence}

Analyze the above and provide your fact-check verdict.""",
    ),
])


def generate(state: GraphState) -> GraphState:
    """
    Perform stance detection and generate the final verdict
    with reasoning based on gathered evidence.
    """
    claim = state["claim"]
    documents = state["documents"]
    route_log = state.get("route_log", [])
    route_log.append("⚖️ Node: GENERATE — Analyzing evidence & producing verdict...")

    # Format evidence for the prompt
    if documents:
        evidence_text = "\n\n".join(
            f"--- Document {i+1} ---\n{doc.page_content}"
            for i, doc in enumerate(documents)
        )
    else:
        evidence_text = "No evidence documents were found for this claim."

    # Generate verdict
    generation_chain = GENERATION_PROMPT | llm | StrOutputParser()
    result = invoke_with_retry(generation_chain, {
        "claim": claim,
        "evidence": evidence_text,
        "current_date": datetime.datetime.now().strftime("%A, %B %d, %Y"),
    })

    route_log.append("   ✅ Verdict generated")

    return {
        **state,
        "generation": result,
        "route_log": route_log,
    }


# ══════════════════════════════════════════════════════════════════
# CONDITIONAL EDGE: Route based on grading result
# ══════════════════════════════════════════════════════════════════

def decide_route(state: GraphState) -> str:
    """
    Conditional edge after grade_documents:
    - If web_search_needed == "yes" → route to web_search
    - Otherwise → route to generate
    """
    if state.get("web_search_needed") == "yes":
        return "web_search"
    return "generate"


# ══════════════════════════════════════════════════════════════════
# BUILD THE GRAPH
# ══════════════════════════════════════════════════════════════════

def build_graph() -> StateGraph:
    """
    Construct and compile the LangGraph CRAG pipeline.

    Flow:
        retrieve → grade_documents →  (relevant)   → generate → END
                                    →  (irrelevant) → web_search → generate → END
    """
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("web_search", web_search)
    workflow.add_node("generate", generate)

    # Set entry point
    workflow.set_entry_point("retrieve")

    # Add edges
    workflow.add_edge("retrieve", "grade_documents")

    # Conditional edge from grade_documents
    workflow.add_conditional_edges(
        "grade_documents",
        decide_route,
        {
            "web_search": "web_search",
            "generate": "generate",
        },
    )

    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", END)

    # Compile the graph
    app = workflow.compile()
    return app


# ── Quick test (if run standalone) ─────────────────────────────────
if __name__ == "__main__":
    print("Building TruthSeeker CRAG graph...")
    graph = build_graph()
    print("✅ Graph compiled successfully!")
    print()

    # Test with a sample claim
    test_claim = "Donald Trump signed a new executive order in 2017"
    print(f"Testing with claim: \"{test_claim}\"")
    print("=" * 60)

    result = graph.invoke({
        "claim": test_claim,
        "documents": [],
        "web_search_needed": "no",
        "source_type": "database",
        "generation": "",
        "route_log": [],
    })

    print("\n--- ROUTING LOG ---")
    for entry in result["route_log"]:
        print(entry)

    print("\n--- RESULT ---")
    print(result["generation"])
