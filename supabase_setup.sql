-- ============================================
-- TruthSeeker — Supabase SQL Setup
-- ============================================
-- Run this ONCE in your Supabase SQL Editor
-- (Dashboard → SQL Editor → New Query → Paste & Run)
-- ============================================

-- 1. Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the documents table
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(384)
);

-- 3. Create an index for faster similarity search
CREATE INDEX IF NOT EXISTS documents_embedding_idx
ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. Create the similarity search function
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(384),
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM documents d
    WHERE d.metadata @> filter
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
