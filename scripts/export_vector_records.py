#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from corpus_pipeline.common import load_json


EMBEDDING_MODEL = "@cf/baai/bge-base-en-v1.5"
EMBEDDING_DIMENSIONS = 768


def embedding_text(record: dict[str, Any]) -> str:
    keywords = ", ".join(record.get("retrieval_metadata", {}).get("keywords", []))
    parts = [
        f"Title: {record.get('title', '')}",
        f"Collection: {record.get('collection', '')}",
        f"Source type: {record.get('source_type', '')}",
        f"Citation: {record.get('citation', '')}",
        f"Keywords: {keywords}",
        "",
        record.get("text", ""),
    ]
    return "\n".join(part for part in parts if part is not None).strip()


def build_vector_record(record: dict[str, Any]) -> dict[str, Any]:
    metadata = {
        "domain": record.get("domain", "content_intelligence"),
        "collection": record.get("collection", "evidence"),
        "corpus_version": record.get("corpus_version", 1),
        "content_hash": record.get("content_hash", ""),
        "embedding_model": record.get("embedding_model", EMBEDDING_MODEL),
        "embedding_dimensions": record.get("embedding_dimensions", EMBEDDING_DIMENSIONS),
        "source_id": record.get("source_id", ""),
        "segment_id": record.get("segment_id", ""),
        "title": record.get("title", ""),
        "source_type": record.get("source_type", ""),
        "citation": record.get("citation", ""),
        "artifact_pipeline": record.get("artifact_pipeline", ""),
        "content_kind": record.get("content_kind", ""),
        "public_safety_level": record.get("public_safety_level", ""),
        "source_visibility": record.get("source_visibility", ""),
        "license_status": record.get("license_status", ""),
        "embedding_status": record.get("embedding_status", ""),
        "keywords": record.get("retrieval_metadata", {}).get("keywords", []),
    }
    return {
        "object_type": "VectorExportRecord",
        "schema_version": 1,
        "id": record["chunk_id"],
        "embedding_text": embedding_text(record),
        "text": record.get("text", ""),
        "metadata": metadata,
    }


def validate_inputs(index: dict[str, Any], review: dict[str, Any]) -> list[dict[str, Any]]:
    if index.get("object_type") != "RagIndex":
        raise ValueError("rag-index input must have object_type=RagIndex")
    if review.get("object_type") != "PublicSafetyReview" or review.get("status") != "pass":
        raise ValueError("public-safety review must pass before vector export")
    records = index.get("records", [])
    if not records:
        raise ValueError("rag-index input has no records")
    unsafe = [record for record in records if record.get("public_safety_level") != "L3_public_safe_derivative"]
    if unsafe:
        raise ValueError(f"vector export blocked: {len(unsafe)} records are not public-safe derivatives")
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export public-safe RAG records for embedding/vector upsert.")
    parser.add_argument("--index", default="sample_outputs/rag-index.json")
    parser.add_argument("--review", default="sample_outputs/public-safety-review.json")
    parser.add_argument("--out", default="sample_outputs/vector-records.jsonl")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    index = load_json(root / args.index)
    review = load_json(root / args.review)
    records = validate_inputs(index, review)
    output_path = root / args.out
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(build_vector_record(record), sort_keys=True) + "\n")
    print(f"wrote {args.out} ({len(records)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
