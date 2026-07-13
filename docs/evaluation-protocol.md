# Evaluation Protocol

The project should evaluate the whole artifact-to-RAG chain, not only final
answer text.

## Local Gates

Run:

```bash
make portfolio-demo
python3 -m py_compile scripts/*.py demos/cloud_video_transcription/run_demo.py demos/ocr_document_cleanup/run_demo.py
```

The demo rebuilds manifests, corpora, report briefs, RAG index records,
public-safety review output, vector export records, information-object maps,
method packs, and object validation.

## Required Checks

- Schema validation for all information objects.
- Public-safety review must pass with zero forbidden pattern hits.
- RAG index record count must match source corpus segments.
- The RAG index must include a deterministic corpus fingerprint.
- Every RAG index record must include domain, collection, citation label,
  direct source provenance, public-safety level, content hash, embedding model,
  dimensions, and pooling mode.
- Every vector export record must include `embedding_text`, answerable text,
  direct source provenance, citation metadata, collection metadata, model and
  pooling metadata, the release corpus fingerprint, and the approved
  public-safety level.
- Reports must cite retrieved evidence.
- Generated outputs must not contain high-confidence secrets or private paths.

## Retrieval Evals

`evals/retrieval-cases.json` defines fixture questions with expected source ids
for workflow, format-boundary, safety, evaluation, and object-model questions.
Run them with:

```bash
make eval
```

The serving release gate adds deterministic refusal, unsupported-scope, corpus
parity, direct-link, latency, and generated-citation checks. Additional fixture
coverage can expand to:

- What does the pipeline do?
- How are transcripts cleaned?
- What prevents private content leakage?
- What evidence supports source-grounded reporting?
- What should the assistant refuse?

Metrics should include recall@k, reciprocal rank, citation presence, and
unsupported-answer detection.

The Worker-side tests should also cover retrieval-path behavior:

- lexical mode when Vectorize bindings are absent
- hybrid mode when `AI` and `CONTENT_RAG_VECTOR_INDEX` bindings are present
- lexical fallback when embedding or Vectorize query execution fails
- refusal behavior for raw private artifact or credential extraction

## Answer Evals

Answer evaluation should check:

- directness
- evidence use
- citation correctness
- uncertainty language
- refusal behavior
- useful follow-up suggestions
- robustness to typos and vague prompts

Model-judged evals can help with qualitative answer quality, but deterministic
privacy, citation, and retrieval checks should remain the release gate.
