"""
TruthSeeker — Data Ingestion Pipeline
======================================
Loads True.csv, chunks articles, generates embeddings,
and inserts everything into Supabase (pgvector).

Usage:
    python ingest.py
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from supabase import create_client, Client

# ── Load environment variables ─────────────────────────────────────
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

# ── Configuration ──────────────────────────────────────────────────
DATA_PATH = os.path.join("data", "True.csv")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 100  # rows per Supabase insert batch
TABLE_NAME = "documents"


def load_dataset(path: str) -> pd.DataFrame:
    """Load True.csv and validate its structure."""
    if not os.path.exists(path):
        print(f"❌ ERROR: Dataset not found at '{path}'")
        print("   Download it from: https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset")
        print("   Extract True.csv into the data/ folder.")
        sys.exit(1)

    df = pd.read_csv(path)
    print(f"✅ Loaded dataset: {len(df)} articles")
    print(f"   Columns: {list(df.columns)}")
    return df


def prepare_documents(df: pd.DataFrame) -> list[dict]:
    """Combine title + text into documents with metadata."""
    documents = []
    for idx, row in df.iterrows():
        # Combine title and text for richer context
        full_text = f"{row['title']}\n\n{row['text']}"
        metadata = {
            "source_index": int(idx),
            "subject": row.get("subject", "unknown"),
            "date": str(row.get("date", "unknown")),
            "title": row["title"][:200],  # truncate for metadata
        }
        documents.append({"text": full_text, "metadata": metadata})

    print(f"✅ Prepared {len(documents)} documents")
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Split documents into smaller chunks using LangChain."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for doc in documents:
        splits = splitter.split_text(doc["text"])
        for i, chunk_text in enumerate(splits):
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    **doc["metadata"],
                    "chunk_index": i,
                    "total_chunks": len(splits),
                },
            })

    print(f"✅ Created {len(chunks)} chunks (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


def generate_embeddings(chunks: list[dict], model_name: str) -> list[list[float]]:
    """Generate vector embeddings for all chunks."""
    print(f"⏳ Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)

    texts = [c["content"] for c in chunks]
    print(f"⏳ Generating embeddings for {len(texts)} chunks (this may take a few minutes)...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    print(f"✅ Generated {len(embeddings)} embeddings (dimension: {len(embeddings[0])})")
    return embeddings.tolist()


def insert_into_supabase(
    supabase: Client,
    chunks: list[dict],
    embeddings: list[list[float]],
    batch_size: int = BATCH_SIZE,
):
    """Batch insert chunks + embeddings into the Supabase documents table."""
    total = len(chunks)
    inserted = 0

    print(f"⏳ Inserting {total} chunks into Supabase (batch_size={batch_size})...")

    for i in range(0, total, batch_size):
        batch = []
        for j in range(i, min(i + batch_size, total)):
            batch.append({
                "content": chunks[j]["content"],
                "metadata": chunks[j]["metadata"],
                "embedding": embeddings[j],
            })

        try:
            supabase.table(TABLE_NAME).insert(batch).execute()
            inserted += len(batch)
            progress = (inserted / total) * 100
            print(f"   📦 Inserted {inserted}/{total} ({progress:.1f}%)")
        except Exception as e:
            print(f"   ❌ Error inserting batch at index {i}: {e}")
            print(f"   Retrying with smaller batch...")
            # Retry one-by-one for failed batch
            for record in batch:
                try:
                    supabase.table(TABLE_NAME).insert(record).execute()
                    inserted += 1
                except Exception as e2:
                    print(f"   ❌ Failed single record: {e2}")

    print(f"✅ Successfully inserted {inserted}/{total} chunks into Supabase")


def main():
    print("=" * 60)
    print("  TruthSeeker — Data Ingestion Pipeline")
    print("=" * 60)
    print()

    # Step 1: Load dataset
    df = load_dataset(DATA_PATH)

    # Step 2: Prepare documents
    documents = prepare_documents(df)

    # Step 3: Chunk documents
    chunks = chunk_documents(documents)

    # Step 4: Generate embeddings
    embeddings = generate_embeddings(chunks, EMBEDDING_MODEL)

    # Step 5: Connect to Supabase
    print("⏳ Connecting to Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase")

    # Step 6: Insert into database
    insert_into_supabase(supabase, chunks, embeddings)

    print()
    print("=" * 60)
    print("  ✅ Ingestion Complete!")
    print(f"  📊 {len(df)} articles → {len(chunks)} chunks → Supabase")
    print("=" * 60)


if __name__ == "__main__":
    main()
