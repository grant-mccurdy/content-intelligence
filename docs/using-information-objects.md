# Using Information Objects

The generated objects are intended to be consumed by downstream tools rather
than read as raw files.

## Search Algorithm

A search step consumes `CorpusSegment` objects. It can rank segments by keyword,
embedding similarity, tags, or any other retrieval method while preserving
`segment_id`, `source_id`, and `citation`.

## RAG Index

A RAG serving layer should consume `RagIndexRecord` objects. These records keep
the source citation fields from `CorpusSegment`, then add public-safety,
licensing, source visibility, and retrieval metadata for vector indexing.

The RAG layer should answer only from retrieved records. If records do not
support the question, it should state the gap and offer a supported follow-up.

## Report Generator

A report generator consumes retrieved segments and emits `EvidenceCitation`
objects. The Markdown report is a presentation layer; `report-brief.json` is the
structured object that preserves questions, evidence, scores, and citations.

## Agent Context

An agent should consume bounded objects, not raw instructional artifacts. A
typical context package would include:

- the user question or task
- a small set of `CorpusSegment` objects
- relevant `RagIndexRecord` objects for retrieval-backed answers
- prior `EvidenceCitation` objects when available
- public-safety or source-use constraints

The agent can then produce a draft answer, report, or next-step recommendation
while retaining auditable links back to source segments.

## Transcript Enrichment

A transcript enrichment step consumes raw transcript excerpts, domain context,
and conservative cleanup rules. It emits `TranscriptEnrichmentPacket` objects
that preserve the prompt contract, allowed edits, correction notes, and
public-safety boundary before cleaned transcript text becomes corpus material.

## Algorithmic Analysis

The same objects can support non-agentic analysis:

- count source types in a manifest
- cluster corpus segments by concept vocabulary
- audit which reports cite which source records
- detect stale or unprocessed artifacts from status fields
