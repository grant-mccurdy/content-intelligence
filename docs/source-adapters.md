# Source Adapters

Source adapters are the ingestion boundary for the content-intelligence system.
They discover or copy artifacts into a private workspace and emit a manifest
record that downstream conversion scripts can trust.

## Adapter Contract

Every adapter should emit source metadata with:

- stable source id or import id
- safe source reference
- artifact type
- source group
- size
- checksum when available
- import status
- conversion status
- public-safety classification

The adapter should not decide what is public-safe. It should preserve enough
metadata for review and downstream washing.

## V1 Private Adapter: Dropbox API

The first private adapter uses Dropbox API extraction for instructional source
artifacts. Its role is to list candidate folders, copy allowed documents or
media into a private workspace, and log sanitized counts instead of exposing
private cloud paths.

Supported artifact classes include:

- PDF notes
- text or Markdown notes
- document exports
- optional media files for transcription workflows

Raw media and raw source files remain private.

## Future Adapter Targets

The same contract can support:

- local folders
- Google Drive
- Canvas/LMS exports
- S3 or Cloudflare R2 buckets
- static public web sources
- manually curated public-domain corpora

The rest of the pipeline should consume the manifest contract, not adapter-
specific filesystem or cloud details.
