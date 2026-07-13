# RAG Architecture

The RAG layer is the serving endpoint for the artifact-to-RAG workflow. It
should use generated information objects instead of raw source files.

## Retrieval Records

`sample_outputs/rag-index.json` demonstrates the retrieval record shape. Each
record includes:

- domain and collection (`content_intelligence`, `evidence` or `method`)
- stable chunk id
- source id
- source title and type
- citation label
- public-safety level
- source visibility
- license status
- corpus version and content hash
- embedding model, dimensions, and pooling mode
- repository-relative source path and direct public source URL
- text
- retrieval metadata

These records can be embedded and loaded into a vector database.

The current export uses `@cf/baai/bge-base-en-v1.5` with `cls` pooling. Document
and query embeddings must use the same pooling mode. The top-level corpus
fingerprint lets live release checks reject stale serving bundles.

`sample_outputs/vector-records.jsonl` exports the same public-safe records in a
line-oriented shape suitable for an embedding/upsert job:

- `id`: stable chunk id
- `embedding_text`: title, collection, source metadata, keywords, and body text
  used by the embedding job
- `text`: answerable public-safe body text
- `metadata`: source path and URL, citation, safety, license, pipeline,
  collection, model, dimension, pooling, corpus fingerprint, content-hash, and
  keyword fields

## Recommended Serving Stack

- Vector database: Cloudflare Vectorize
- Runtime: Cloudflare Worker
- Embeddings: Workers AI embeddings or another low-cost embedding provider
- Current fallback: lexical retrieval over the generated corpus

This matches the existing Cloudflare deployment pattern used elsewhere in the
portfolio and keeps the public demo cost low.

## Query Flow

```text
visitor question
-> classify safety and scope
-> embed query
-> retrieve vector candidates
-> optionally blend lexical candidates
-> optionally rerank
-> synthesize answer from cited chunks
-> return citations, limits, confidence, and follow-ups
```

## Answer Rules

- Cite every substantive claim.
- Distinguish evidence from inference.
- Refuse private data extraction or raw source reproduction.
- Say when the indexed corpus is insufficient.
- Offer specific follow-up questions that are supported by the corpus.

## Current Status

The public repo currently implements retrieval-ready index records, a Vectorize
export, local keyword search, generated safety checks, and method/evidence
collections. The portfolio Worker has a Content RAG route over the generated
index. When the `CONTENT_RAG_VECTOR_INDEX` and `AI` bindings are configured,
the route can run hybrid vector-plus-lexical retrieval; otherwise it falls back
to lexical retrieval over the same public-safe records.

`serving/content-rag-core.mjs` is the public source of truth for the portable
serving logic. The private deployment bundle copies that module and supplies
Cloudflare/OpenAI bindings, credentials, CORS, rate limiting, and transport.
