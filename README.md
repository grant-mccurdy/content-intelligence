# Content Intelligence

Artifact-to-RAG pipeline for turning disparate source material into
provenance-rich information objects and source-grounded answers.

## Project Links

- [Try the live cited RAG demo](https://grant-mccurdy.github.io/projects/content-intelligence.html#live-rag)
- [Read the portfolio brief](https://grant-mccurdy.github.io/projects/content-intelligence.html)
- [Review the pipeline case study](https://grant-mccurdy.github.io/case-studies/content-intelligence.html)
- [Inspect the generated demo report](https://grant-mccurdy.github.io/projects/content-intelligence-demo-report.html)

The public workflow standardizes synthetic text, transcript-derived, and
OCR-derived content into one auditable object chain:

```text
source inventory
-> manifest and checksum
-> normalized artifact
-> citation-preserving corpus segments
-> public-safety review
-> retrieval index and vector records
-> hybrid RAG answer with citations and limits
```

The live public service retrieves from safety-reviewed method and evidence
records, combines vector and lexical results, returns source links, and states
its limits when the indexed corpus is insufficient.

## What Is Implemented

The repository is deliberately precise about implemented versus extensible
input support:

| Input or layer | Public implementation |
| --- | --- |
| Plain text | Direct manifesting, normalization, segmentation, retrieval, and reporting. |
| Transcript-derived text | Synthetic staged media/transcript workflow with enrichment packets and cleaned corpus objects. |
| OCR-derived text | Synthetic page-level OCR cleanup workflow with normalized output and corpus objects. |
| Markdown documentation | Chunked as public method evidence for retrieval. |
| PDF, DOCX, and HTML conversion | Adapter contract documented; direct public converters are deferred. |
| Cloud and LMS sources | Dropbox pattern documented from a private prototype; public Google Drive, Canvas, S3/R2, and web adapters are deferred. |
| Retrieval | Local lexical search plus a public hybrid vector/lexical RAG service. |
| Evaluation | Deterministic schema, privacy, citation, retrieval-input, vector-export, retrieval-fixture, and serving-path checks; live answer checks run in the serving release gate. |

The public demo does not claim to ingest arbitrary file formats. It proves the
normalization, provenance, safety, retrieval, and reporting contracts that
format-specific converters can target.

## What The Project Proves

### A standard information-object model

Each stage emits a small structured object rather than passing ad hoc raw files
between scripts:

- `SourceManifestRecord`
- `NormalizedArtifact`
- `TranscriptEnrichmentPacket`
- `CorpusSegment`
- `RagIndexRecord`
- `VectorExportRecord`
- `EvidenceCitation`
- `ReportBrief`
- `AnalysisMethodPack`

Stable source IDs, checksums, citations, transformation status, safety levels,
content hashes, direct public source links, corpus fingerprints, and embedding
metadata keep downstream outputs traceable.

### Public-safety gates before retrieval

Raw private artifacts are not valid retrieval inputs. The build checks generated
records for private paths, identifying data, credential patterns, private course
codes, and unreviewed source boundaries before vector export.

### Source-grounded RAG

`sample_outputs/rag-index.json` and `sample_outputs/vector-records.jsonl`
contain the same reviewed records used by the serving pattern and declare BGE
`cls` pooling explicitly. The public
portfolio Worker supports hybrid vector-plus-lexical retrieval when Cloudflare
bindings are available and a lexical fallback over the same bounded corpus.

Every answer should:

- cite the records supporting substantive claims;
- distinguish evidence from inference;
- state when the corpus is insufficient;
- refuse requests for raw private artifacts or credentials;
- offer follow-up questions supported by the indexed material.

The portable logic used by the deployment bundle is inspectable in
`serving/content-rag-core.mjs`. It defines the public request classifier, query
expansion, hybrid rank fusion, Responses API request contract, prompt/source
fencing, and citation validator. Provider credentials and unrelated private
backend routes remain outside this public repository.

## Rebuild The Public Demo

The local pipeline uses Python and keeps the core demo offline:

```bash
make portfolio-demo
make search QUERY="feedback rubric evidence"
```

`make portfolio-demo` rebuilds and validates:

- source manifests and corpus segments;
- transcript and OCR demonstration objects;
- the cited demo report and report brief;
- the RAG index and vector export;
- the information-object map and method pack;
- the generated public-safety review.
- five deterministic retrieval fixtures with expected source records.
- the public serving-core contract tests.

Run syntax and object validation directly:

```bash
python3 -m py_compile corpus_pipeline/*.py scripts/*.py \
  demos/cloud_video_transcription/run_demo.py \
  demos/ocr_document_cleanup/run_demo.py
make validate
make eval
```

## Reviewer Path

1. Try the live RAG presets on the portfolio page.
2. Inspect `sample_outputs/rag-index.json` for retrieval records and citations.
3. Inspect `sample_outputs/public-safety-review.json` for the release gate.
4. Read `docs/artifact-to-rag-workflow.md` for the end-to-end architecture.
5. Inspect `serving/content-rag-core.mjs` for the live route's portable logic.
6. Read `docs/evaluation-protocol.md` for deterministic and live quality checks.
7. Run `make portfolio-demo` to reproduce the committed public outputs.

## Repository Layout

```text
content-intelligence/
|-- corpus_pipeline/   # Shared normalization and tokenization helpers
|-- data/synthetic/    # Public-safe source fixtures
|-- demos/             # Transcript and OCR-derived workflow simulations
|-- docs/              # Architecture, contracts, safety, and evaluation
|-- method_pack/       # Bounded source-use and reporting rules
|-- reports/           # Current architecture and deployment status
|-- sample_outputs/    # Reviewed generated information objects
|-- schemas/           # Example object contracts
|-- scripts/           # Build, retrieval, export, and validation commands
`-- screenshots/       # Recruiter-facing live-demo evidence
```

## Public-Safety Boundary

The committed demo uses synthetic and public-safe material only. Raw lecture
media, private transcripts, private notes, cloud paths, course identifiers,
student or personnel data, copyrighted source content without permission,
credentials, and API tokens must remain outside this repository and its vector
index.

## Current Status

The public repository builds validated retrieval and vector-export records, and
the portfolio site exposes a working cited RAG interface over the public-safe
corpus. Local release gates include retrieval fixtures, serving-path tests,
generated-answer checks, and corpus-parity validation. The highest-value next
feature is genuine PDF, DOCX, HTML, Markdown, and text conversion into the
existing `NormalizedArtifact` contract, followed by broader fixture coverage
and the synchronized `v2` deployment.
