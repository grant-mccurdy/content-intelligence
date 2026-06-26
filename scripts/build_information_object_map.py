#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path, default: Any) -> Any:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def count_manifest_sources(path: Path) -> int:
    manifest = load_json(path, {})
    return len(manifest.get("sources", manifest.get("files", manifest.get("pages", []))))


def count_corpus_segments(path: Path) -> int:
    corpus = load_json(path, {})
    return int(corpus.get("segment_count") or len(corpus.get("segments", [])))


def count_enrichment_packets(path: Path) -> int:
    return len(list(path.glob("*.json"))) if path.exists() else 0


def count_rag_records(path: Path) -> int:
    rag_index = load_json(path, {})
    return int(rag_index.get("chunk_count") or len(rag_index.get("records", [])))


def count_jsonl_records(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def build_map(root: Path) -> dict[str, Any]:
    report_brief = load_json(root / "sample_outputs" / "report-brief.json", {})
    evidence = report_brief.get("evidence_citations", [])
    rag_records = count_rag_records(root / "sample_outputs" / "rag-index.json")
    vector_records = count_jsonl_records(root / "sample_outputs" / "vector-records.jsonl")
    pipelines = [
        {
            "pipeline": "synthetic_text_sources",
            "source_manifest_records": count_manifest_sources(root / "data" / "processed" / "manifest.json"),
            "normalized_artifacts": count_manifest_sources(root / "data" / "processed" / "manifest.json"),
            "corpus_segments": count_corpus_segments(root / "data" / "processed" / "corpus.json"),
            "evidence_citations": len(evidence),
            "report_briefs": 1 if report_brief else 0,
        },
        {
            "pipeline": "cloud_video_transcription",
            "source_manifest_records": count_manifest_sources(root / "sample_outputs" / "cloud_video_transcription" / "manifest.json"),
            "normalized_artifacts": count_manifest_sources(root / "sample_outputs" / "cloud_video_transcription" / "manifest.json"),
            "transcript_enrichment_packets": count_enrichment_packets(root / "sample_outputs" / "cloud_video_transcription" / "enrichment_packets"),
            "corpus_segments": count_corpus_segments(root / "sample_outputs" / "cloud_video_transcription" / "corpus.json"),
            "evidence_citations": 0,
            "report_briefs": 0,
        },
        {
            "pipeline": "ocr_document_cleanup",
            "source_manifest_records": count_manifest_sources(root / "sample_outputs" / "ocr_document_cleanup" / "manifest.json"),
            "normalized_artifacts": count_manifest_sources(root / "sample_outputs" / "ocr_document_cleanup" / "manifest.json"),
            "corpus_segments": count_corpus_segments(root / "sample_outputs" / "ocr_document_cleanup" / "corpus.json"),
            "evidence_citations": 0,
            "report_briefs": 0,
        },
        {
            "pipeline": "rag_index",
            "source_manifest_records": 0,
            "normalized_artifacts": 0,
            "corpus_segments": rag_records,
            "rag_index_records": rag_records,
            "vector_export_records": vector_records,
            "evidence_citations": 0,
            "report_briefs": 0,
        },
    ]
    return {
        "schema_version": 1,
        "object_type": "InformationObjectMap",
        "description": "Synthetic demo map showing how instructional artifacts become analysis-ready data objects.",
        "object_families": [
            "SourceManifestRecord",
            "NormalizedArtifact",
            "TranscriptEnrichmentPacket",
            "CorpusSegment",
            "EvidenceCitation",
            "ReportBrief",
            "RagIndexRecord",
            "VectorExportRecord",
        ],
        "pipelines": pipelines,
        "public_safety": {
            "uses_synthetic_sources": True,
            "contains_private_content": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a map of generated information objects.")
    parser.add_argument("--out", default="sample_outputs/information-object-map.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    payload = build_map(root)
    write_json(root / args.out, payload)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
