# Artifact-To-RAG Workflow

This project is designed around a reusable artifact-to-RAG workflow. The public
repo uses synthetic inputs, while the private upstream can use real source
adapters such as Dropbox API extraction.

```text
source adapters
-> raw artifact inventory
-> source manifests
-> conversion and conservative cleaning
-> public-safety washing
-> information objects
-> retrieval-ready chunks
-> vector index
-> source-grounded RAG
-> evaluation
```

## 1. Source Adapters

Source adapters discover and copy source artifacts into a controlled private
workspace. The first private adapter uses the Dropbox API for PDFs, text files,
documents, and optional media. Future adapters can target local folders, Google
Drive, Canvas/LMS exports, S3/R2 buckets, or public web sources.

Adapter output should be metadata-first: source path or safe reference, artifact
type, source group, checksum, size, import status, and review status.

## 2. Manifesting

Manifests are the audit layer. They preserve source identity before any model,
cleanup, or retrieval step runs.

The manifest layer should answer:

- What source artifact exists?
- Where did it come from?
- What kind of artifact is it?
- Has it been copied, cleaned, reviewed, or excluded?
- Which derivative objects point back to it?

## 3. Conversion And Cleaning

Conversion turns raw or semi-raw artifacts into cleaned text:

- transcript cleanup for lecture/media artifacts
- OCR cleanup for PDF/image artifacts
- Markdown or text normalization for notes and planning documents

Cleaning is conservative. It improves readability while preserving meaning,
order, and uncertainty markers.

## 4. Public-Safety Washing

Washing happens before public export or vector indexing. It blocks raw private
content, identifying metadata, private paths, credentials, private course
identifiers, and copyrighted source text that lacks permission.

The public demo emits `sample_outputs/public-safety-review.json` as a concrete
safety gate for retrieval-ready records.

## 5. Information Objects

The workflow promotes cleaned material into stable objects:

- `SourceManifestRecord`
- `NormalizedArtifact`
- `TranscriptEnrichmentPacket`
- `CorpusSegment`
- `EvidenceCitation`
- `ReportBrief`
- `RagIndexRecord`
- `AnalysisMethodPack`

These objects make the RAG layer auditable because every answer can point back
to a known source segment.

## 6. Retrieval And RAG

The public demo builds `sample_outputs/rag-index.json`, a retrieval-ready set
of source-grounded chunks, and `sample_outputs/vector-records.jsonl`, a
Vectorize-ready export with embedding text and metadata. The portfolio Worker
can retrieve semantically from Cloudflare Vectorize when the vector and Workers
AI bindings are configured, then blend those candidates with lexical matches.
When vector retrieval is unavailable, it falls back to lexical retrieval over
the same public-safe records.

RAG should be bounded by the corpus. If the evidence is missing, the assistant
should say so and suggest a supported follow-up instead of inventing context.

## 7. Evaluation

The pipeline should be tested at each layer:

- schema validation
- privacy and secret scanning
- conversion quality
- retrieval relevance
- citation grounding
- refusal behavior
- live RAG stability

The goal is a visitor-facing assistant that feels useful because the underlying
source chain is explicit and testable.
