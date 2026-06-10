# Artifact Conversion And Agent Context Status

Date: 2026-06-06

## Summary

The next useful development direction is to generate agent context packets from
instructional information artifacts. Before that, the project still needs a
unified artifact conversion layer that can turn cleaned PDF/OCR outputs and
cleaned lecture transcript text into consistent, validated information objects.

The current repo has strong public-safe demos and object models, but it does not
yet have a general ingestion script for real cleaned instructional artifacts.

## What Exists In `content-intelligence`

The public repo currently includes portfolio-safe demonstrations of:

- synthetic text source processing
- cloud video-to-transcript workflow simulation
- simulated OpenAI-style transcript enrichment
- OCR document cleanup simulation
- source manifest generation
- corpus segment generation
- source-grounded report brief generation
- AI-readable analysis method pack generation
- information object validation

The current information object chain is:

```text
instructional artifacts
-> SourceManifestRecord
-> NormalizedArtifact
-> TranscriptEnrichmentPacket
-> CorpusSegment
-> EvidenceCitation
-> ReportBrief
-> AnalysisMethodPack
```

These artifacts are designed to guide agent behavior: preserve provenance,
distinguish evidence from inference, label uncertainty, avoid unsupported
claims, and consume bounded source objects instead of raw instructional
materials.

## What Exists In `ms-statistics`

The private `ms-statistics` repo contains the operational workflows that inspired
the public project:

- `scripts/pdf_to_png.sh`: converts PDFs into page images.
- `scripts/mathpix_batch.py`: sends PDF/page-image artifacts through Mathpix OCR.
- `scripts/latex_cleanup_openai.py`: cleans OCR/LaTeX output through OpenAI.
- `scripts/dropbox_lecture_transcribe.py`: lists/downloads Dropbox lecture media,
  extracts audio chunks, generates raw transcripts, and creates cleaned
  transcripts through OpenAI.

Those scripts are useful as private source patterns, but they should not be
copied directly into the public repo without sanitization and redesign.

## Missing Piece

The missing tool is a unified artifact conversion script.

It should consume already-cleaned public-safe artifacts such as:

- cleaned lecture transcript `.txt` files
- cleaned OCR/PDF-derived `.txt`, `.md`, or `.tex` files
- synthetic or public-license source documents

It should emit structured information objects such as:

```text
source_manifest.json
normalized_artifacts.json
corpus_segments.json
artifact_index.json
public_safety_review.json
```

This conversion layer should come before a general agent context packet
generator. Otherwise, the context packet generator will not have stable source
objects to consume.

## Recommended Build Sequence

1. Build an artifact conversion script.

   The script should normalize cleaned text artifacts into source manifest
   records, normalized artifact records, corpus segments, and a lightweight
   artifact index.

2. Build an agent context packet generator.

   The generator should consume the method pack, selected corpus segments,
   source-use rules, current project state, and a user task to produce:

   ```text
   agent_context_packet.json
   agent_context_packet.md
   ```

3. Use the packet generator in a real adjacent project.

   A good first target is the longitudinal model work in:

   ```text
   /home/grant/repos/public/synthetic-education-data
   ```

   The packet should combine content-intelligence method rules with the current
   synthetic education data methodology and the task of designing longitudinal
   assignment transitions after Assignment 02.

## Design Guidance For The Agent Packet

The packet should tell the agent to:

- preserve provenance
- cite source objects when making recommendations
- distinguish evidence from inference
- mark assumptions explicitly
- avoid inventing hidden calibration data
- keep public-safety constraints visible
- produce implementation plans that can be validated

For the longitudinal model task, the packet should ask for:

- model philosophy
- latent variables
- score generation process
- missingness and attendance process
- course, track, teacher, and section effects
- validation checks
- public-safety constraints
- implementation plan
- open design questions

## Current Conclusion

The agent context packet generator is the right next strategic tool, but the
artifact conversion/normalization script should be built first. The conversion
script creates the reliable information objects; the packet generator then
selects and packages those objects for agent-assisted development.
