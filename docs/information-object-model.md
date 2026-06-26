# Information Object Model

This project turns instructional artifacts into analysis-ready information
objects. The objects are intentionally small, structured, and provenance-aware
so they can feed search, reporting, algorithmic analysis, agent context, or a
source-grounded RAG service.

```text
instructional artifacts
-> SourceManifestRecord
-> NormalizedArtifact
-> TranscriptEnrichmentPacket
-> CorpusSegment
-> RagIndexRecord
-> EvidenceCitation
-> ReportBrief
```

## Core Objects

### SourceManifestRecord

Identifies a source artifact before analysis. It records source identity, type,
license or public-safety status, checksum when available, and processing status.

### NormalizedArtifact

Represents a cleaned text artifact derived from an original source. Examples
include cleaned transcript excerpts, OCR-cleaned notes, or normalized synthetic
source documents.

### TranscriptEnrichmentPacket

Captures the guarded transcript cleanup step between raw machine transcription
and corpus construction. It records the prompt contract, domain context, allowed
edits, disallowed edits, correction notes, and public-safety metadata.

### CorpusSegment

Stores a source-preserving text segment with a stable segment ID, source ID,
title, source type, text, and citation label.

### RagIndexRecord

Packages a public-safe corpus segment for retrieval and vector indexing. It
adds a stable chunk ID, public-safety level, source visibility, license status,
embedding status, and retrieval metadata.

### EvidenceCitation

Links a downstream question or claim to a supporting corpus segment. This is the
bridge between retrieval and auditable reports or agent context.

### ReportBrief

Packages generated analysis around questions and cited evidence. A report brief
can be rendered as Markdown, passed to an agent, or used by an algorithmic
review workflow.

## Design Rules

- Every object should keep enough provenance to trace back to a source record.
- Public examples must use synthetic or licensed sources.
- Private raw artifacts should not be copied into public objects.
- RAG index records should contain only public-safe derivatives.
- Downstream analysis should consume objects, not ad hoc raw files.
