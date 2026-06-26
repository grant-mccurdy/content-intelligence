# Reporting Rules

Reports and RAG answers should be evidence-first. The process is:

```text
question
-> retrieve CorpusSegment or RagIndexRecord objects
-> produce EvidenceCitation objects
-> write ReportBrief narrative or RAG response
-> preserve citation links
```

Rules:

- Every substantive claim needs cited evidence.
- Inference must be labeled as inference.
- Missing evidence should be reported as a gap, not filled in.
- The Markdown report is presentation; `ReportBrief` or a cited RAG response is
  the structured output.
