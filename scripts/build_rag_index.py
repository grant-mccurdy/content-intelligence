#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from corpus_pipeline.common import load_json, read_text, slugify, tokenize, write_json


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "or",
    "that",
    "the",
    "to",
    "with",
}

CORPUS_INPUTS = [
    ("synthetic_text_sources", "data/processed/corpus.json", "synthetic source document"),
    ("cloud_video_transcription", "sample_outputs/cloud_video_transcription/corpus.json", "clean transcript excerpt"),
    ("ocr_document_cleanup", "sample_outputs/ocr_document_cleanup/corpus.json", "clean OCR note"),
]

METHOD_INPUTS = [
    ("README.md", "Content Intelligence README"),
    ("docs/artifact-to-rag-workflow.md", "Artifact-to-RAG Workflow"),
    ("docs/source-adapters.md", "Source Adapter Contract"),
    ("docs/rag-architecture.md", "RAG Architecture"),
    ("docs/evaluation-protocol.md", "Evaluation Protocol"),
    ("docs/information-object-model.md", "Information Object Model"),
    ("docs/pipeline-overview.md", "Pipeline Overview"),
    ("docs/source-grounding.md", "Source Grounding"),
    ("docs/using-information-objects.md", "Using Information Objects"),
    ("docs/workflow-diagram.md", "Workflow Diagram"),
    ("docs/privacy-and-copyright.md", "Privacy And Copyright Boundary"),
    ("reports/artifact-conversion-and-agent-context-status.md", "Artifact Conversion Status"),
    ("method_pack/reporting-rules.md", "Reporting Rules"),
    ("method_pack/source-use-policy.md", "Source Use Policy"),
]

FORBIDDEN_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "local_home_path": re.compile(r"/home/[A-Za-z0-9._/-]+"),
    "windows_user_path": re.compile(r"[A-Za-z]:\\Users\\[^\\]+"),
    "dropbox_url_or_token": re.compile(r"dropbox(?:api)?\.com|" + "DROPBOX" + r"_API_KEY", re.IGNORECASE),
    "openai_key": re.compile(r"\b" + "sk-" + r"[A-Za-z0-9_-]{20,}\b"),
    "private_course_code": re.compile(r"\bMATH[- ]?\d{3}\b", re.IGNORECASE),
}


def top_keywords(text: str, limit: int = 8) -> list[str]:
    counts = Counter(term for term in tokenize(text) if term not in STOPWORDS and len(term) > 2)
    return [term for term, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chunk_text(text: str, max_chars: int = 650) -> list[str]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n")) if block.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for block in blocks:
        block_len = len(block)
        if current and current_len + block_len + 2 > max_chars:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        if block_len > max_chars:
            sentences = re.split(r"(?<=[.!?])\s+", block)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if current and current_len + len(sentence) + 1 > max_chars:
                    chunks.append("\n\n".join(current))
                    current = []
                    current_len = 0
                current.append(sentence)
                current_len += len(sentence) + 1
            continue
        current.append(block)
        current_len += block_len + 2
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def base_record(**kwargs: Any) -> dict[str, Any]:
    text = kwargs["text"]
    return {
        "object_type": "RagIndexRecord",
        "schema_version": 1,
        "domain": "content_intelligence",
        "corpus_version": 1,
        "content_hash": content_hash(text),
        "embedding_model": "@cf/baai/bge-base-en-v1.5",
        "embedding_dimensions": 768,
        "public_safety_level": "L3_public_safe_derivative",
        "source_visibility": kwargs.get("source_visibility", "public_demo_synthetic"),
        "license_status": kwargs.get("license_status", "synthetic_demo"),
        "embedding_status": "ready_for_embedding",
        "retrieval_metadata": {
            "keywords": top_keywords(text),
            "character_count": len(text),
        },
        **kwargs,
    }


def load_evidence_segments(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for pipeline, rel_path, content_kind in CORPUS_INPUTS:
        path = root / rel_path
        corpus = load_json(path)
        for segment in corpus.get("segments", []):
            chunk_id = f"{pipeline}:{segment['segment_id']}"
            text = segment.get("text", "")
            records.append(
                base_record(
                    chunk_id=chunk_id,
                    segment_id=segment["segment_id"],
                    source_id=segment["source_id"],
                    title=segment["title"],
                    source_type=segment["source_type"],
                    citation=segment["citation"],
                    text=text,
                    artifact_pipeline=pipeline,
                    content_kind=content_kind,
                    collection="evidence",
                )
            )
    return records


def load_method_segments(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for relative_path, title in METHOD_INPUTS:
        path = root / relative_path
        if not path.exists():
            continue
        source_id = slugify(relative_path.replace("/", "-").replace(".md", ""), "method-source")
        for index, text in enumerate(chunk_text(read_text(path)), start=1):
            segment_id = f"{source_id}#{index:02d}"
            records.append(
                base_record(
                    chunk_id=f"method:{segment_id}",
                    segment_id=segment_id,
                    source_id=source_id,
                    title=title,
                    source_type="public method documentation",
                    citation=f"{title}, section {index}",
                    text=text,
                    artifact_pipeline="method_documentation",
                    content_kind="method documentation",
                    collection="method",
                    source_visibility="public_repo_documentation",
                    license_status="public_repo_demo",
                )
            )
    return records


def load_segments(root: Path) -> list[dict[str, Any]]:
    return load_evidence_segments(root) + load_method_segments(root)


def build_public_safety_review(records: list[dict[str, Any]]) -> dict[str, Any]:
    hits = []
    for record in records:
        text = "\n".join(
            str(record.get(field, ""))
            for field in ["chunk_id", "source_id", "title", "source_type", "citation", "text"]
        )
        for name, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                hits.append({"chunk_id": record["chunk_id"], "rule": name})
    return {
        "object_type": "PublicSafetyReview",
        "schema_version": 1,
        "status": "pass" if not hits else "fail",
        "checked_records": len(records),
        "forbidden_pattern_hits": hits,
        "rules": sorted(FORBIDDEN_PATTERNS),
    }


def build_rag_index(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "object_type": "RagIndex",
        "schema_version": 1,
        "description": "Public-safe retrieval-ready records for the artifact-to-RAG demo.",
        "chunk_count": len(records),
        "collections": {
            "evidence": sum(1 for record in records if record.get("collection") == "evidence"),
            "method": sum(1 for record in records if record.get("collection") == "method"),
        },
        "embedding_status": "not_embedded_public_demo",
        "embedding_model": "@cf/baai/bge-base-en-v1.5",
        "embedding_dimensions": 768,
        "vector_database_target": "Cloudflare Vectorize",
        "records": records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build public-safe retrieval records for RAG indexing.")
    parser.add_argument("--out", default="sample_outputs/rag-index.json")
    parser.add_argument("--review-out", default="sample_outputs/public-safety-review.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    records = load_segments(root)
    review = build_public_safety_review(records)
    if review["status"] != "pass":
        for hit in review["forbidden_pattern_hits"]:
            print(f"public-safety hit: {hit['chunk_id']} {hit['rule']}", file=sys.stderr)
        return 1
    write_json(root / args.out, build_rag_index(records))
    write_json(root / args.review_out, review)
    print(f"wrote {args.out} ({len(records)} records)")
    print(f"wrote {args.review_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
