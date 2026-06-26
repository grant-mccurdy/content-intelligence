# Privacy And Copyright

This repository is public-facing. It must not contain:

- private lecture transcripts
- private Dropbox paths
- private cloud storage URLs
- professor, student, or class-identifying transcript content
- raw meeting notes from private institutions
- student names, grades, submissions, or feedback records
- OAuth tokens, API keys, `.env` files, or credential JSON
- copyrighted source text without permission or license clarity

Safe demo sources include:

- synthetic notes written for the demo
- public-domain texts
- permissively licensed texts with attribution
- short user-authored examples that do not identify private people or
  institutions

When adapting private workflows, copy architecture and implementation patterns,
not private content.

## Promotion Boundary

Use this promotion path:

```text
private raw artifact
-> private manifest
-> private cleaned derivative
-> public-safety review
-> synthetic or reviewed public-safe object
-> retrieval index
```

The public RAG index should contain only L3 public-safe derivatives. If a source
cannot be safely summarized or synthesized, leave it out of the public index.
