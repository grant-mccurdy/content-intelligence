# Source Grounding

Every generated segment carries:

- `segment_id`
- `source_id`
- source title
- source type
- citation label
- original segment text

Reports should cite the segment that supports each claim. A report generator
should not make claims that cannot be traced back to retrieved source material.

The RAG index extends this contract. Every `RagIndexRecord` carries the source
segment id, citation label, public-safety level, domain, collection, content
hash, embedding metadata, text, and retrieval metadata. That means a RAG answer
can cite the retrieved chunk instead of relying on unverifiable prompt context.

For serving, the public scaffold keeps keyword search because it is transparent
and easy to audit, emits `sample_outputs/vector-records.jsonl` for Cloudflare
Vectorize loading, and lets the portfolio Worker use vector-plus-lexical
retrieval when bindings are configured. Passage-level citation spans and
reranking remain useful future quality layers.
