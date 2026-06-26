# Content Intelligence

Artifact-to-RAG pipeline for source-grounded instructional intelligence.

This repository demonstrates the public-safe version of a private workflow that
starts with source artifacts and ends with retrieval-ready evidence for a RAG
assistant. The first private source adapter uses Dropbox API extraction, but the
public project is intentionally source-agnostic: the same pattern can support
local folders, Google Drive, Canvas/LMS exports, S3/R2 buckets, or public web
sources.

```text
source adapters
-> raw artifact inventory
-> source manifests
-> conversion and conservative cleaning
-> public-safety washing
-> information objects
-> retrieval-ready chunks
-> vector index target
-> source-grounded RAG
-> evaluation
```

The committed demo uses synthetic and public-safe material only. Raw lecture
media, private transcripts, private notes, Dropbox paths, course identifiers,
and identifying metadata stay outside this public repository.

## What This Project Demonstrates

- Source-adapter design for private artifact extraction
- Manifest-first provenance and checksum tracking
- Transcript and OCR/document cleanup workflows
- Public-safety washing before publication or indexing
- Analysis-ready information objects
- Citation-preserving corpus segmentation
- Retrieval-ready RAG index records
- Source-grounded report generation
- AI-readable method packs for bounded agent behavior
- Validation for schema, privacy, retrieval inputs, and evidence contracts

## Current Vs Next

| Layer | Current status |
| --- | --- |
| Source adapters | Private Dropbox/source import scripts exist outside this public repo; this repo documents the adapter contract. |
| Conversion demos | Synthetic transcript, OCR, and source-note examples are implemented. |
| Information objects | Manifest, corpus, citation, report, method-pack, and RAG index objects are generated and validated. |
| Retrieval | Keyword search, retrieval-ready `rag-index.json`, and Cloudflare Vectorize export records are implemented. |
| Vector database | Cloudflare Vectorize is the recommended target; records include model, dimension, collection, and content-hash metadata for loading. |
| RAG service | The portfolio Worker exposes a Content RAG route that can use Vectorize when configured and falls back to lexical retrieval over the same public-safe index. |
| Evaluation | Schema, object, privacy, generated-artifact, retrieval-input, vector-export, and Worker retrieval-path validation are implemented; answer-quality evals remain the next quality layer. |

## Reviewer Path

1. Read `docs/artifact-to-rag-workflow.md` for the end-to-end architecture.
2. Read `docs/source-adapters.md` for the generic adapter contract and Dropbox
   v1 pattern.
3. Inspect `sample_outputs/rag-index.json` to see the retrieval-ready records.
4. Inspect `sample_outputs/public-safety-review.json` to see the safety gate.
5. Read `docs/rag-architecture.md` and `docs/evaluation-protocol.md` for the
   hybrid vector/lexical serving layer and tests.
6. Run `make portfolio-demo` to rebuild and validate the public-safe demo.

## Generated Objects

The demo builds:

- `data/processed/manifest.json`
- `data/processed/corpus.json`
- `sample_outputs/demo-report.md`
- `sample_outputs/report-brief.json`
- `sample_outputs/rag-index.json`
- `sample_outputs/public-safety-review.json`
- `sample_outputs/vector-records.jsonl`
- `sample_outputs/information-object-map.json`
- `sample_outputs/analysis-method-pack.json`

The canonical method contract is `sample_outputs/analysis-method-pack.json`.
It tells an agent or algorithm how to retrieve source objects, cite evidence,
preserve uncertainty, and avoid private source leakage.

## Quick Demo

The public scaffold is offline and standard-library only.

```bash
make portfolio-demo
make search QUERY="feedback rubric evidence"
```

Direct Python equivalent:

```bash
python3 scripts/build_manifest.py
python3 scripts/build_corpus.py
python3 scripts/generate_report.py
python3 demos/cloud_video_transcription/run_demo.py
python3 demos/ocr_document_cleanup/run_demo.py
python3 scripts/build_rag_index.py
python3 scripts/export_vector_records.py
python3 scripts/build_information_object_map.py
python3 scripts/build_analysis_method_pack.py
python3 scripts/validate_information_objects.py
```

## Project Structure

```text
content-intelligence/
├── corpus_pipeline/
├── data/
├── demos/
│   ├── cloud_video_transcription/
│   └── ocr_document_cleanup/
├── docs/
│   ├── artifact-to-rag-workflow.md
│   ├── source-adapters.md
│   ├── rag-architecture.md
│   └── evaluation-protocol.md
├── method_pack/
├── reports/
├── sample_outputs/
├── schemas/
└── scripts/
```

## Public Safety Rules

Do not publish professor names, university course identifiers, private LMS
links, copyrighted transcripts, raw lecture text, video URLs, private lecture
manifests, private Dropbox paths, credentials, or coursework-specific prompts.

Public examples should use synthetic transcripts, synthetic notes,
public-domain material, permissively licensed material, or manually reviewed
public-safe derivatives.

## Portfolio Framing

The value is not a chatbot alone. The value is the system that converts messy
instructional artifacts into safe, auditable, retrievable evidence objects and
then serves those objects through a bounded RAG interface.
