#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def existing_references(root: Path, paths: list[str]) -> list[dict[str, Any]]:
    refs = []
    for rel in paths:
        path = root / rel
        refs.append(
            {
                "path": rel,
                "exists": path.exists(),
                "kind": path.suffix.lstrip(".") or "directory",
            }
        )
    return refs


def build_pack(root: Path) -> dict[str, Any]:
    source = load_json(root / "method_pack" / "analysis-method-pack.json")
    generated = dict(source)
    generated["generated_artifacts"] = existing_references(
        root,
        [
            "sample_outputs/information-object-map.json",
            "sample_outputs/report-brief.json",
            "sample_outputs/cloud_video_transcription/corpus.json",
            "sample_outputs/cloud_video_transcription/transcript_enrichment_brief.md",
            "sample_outputs/ocr_document_cleanup/corpus.json",
            "sample_outputs/rag-index.json",
            "sample_outputs/public-safety-review.json",
        ],
    )
    generated["human_readable_companions"] = existing_references(
        root,
        [
            "method_pack/reporting-rules.md",
            "method_pack/source-use-policy.md",
            "method_pack/example-context.md",
        ],
    )
    generated["task_contract"] = {
        "task": "Generate a source-grounded instructional analysis brief or RAG response.",
        "inputs": ["SourceManifestRecord[]", "CorpusSegment[]", "RagIndexRecord[]"],
        "outputs": ["EvidenceCitation[]", "ReportBrief"],
        "required_behavior": [
            "retrieve relevant source-preserving segments",
            "cite every substantive claim",
            "mark inference and uncertainty",
            "refuse to use private or unsupported context",
        ],
    }
    return generated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the AI-readable analysis method pack.")
    parser.add_argument("--out", default="sample_outputs/analysis-method-pack.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    pack = build_pack(root)
    write_json(root / args.out, pack)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
