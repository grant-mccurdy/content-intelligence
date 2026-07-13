#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "SourceManifestRecord": {"source_id", "title", "source_type", "status"},
    "NormalizedArtifact": {"artifact_id", "source_id", "transform", "status"},
    "TranscriptEnrichmentPacket": {
        "object_type",
        "schema_version",
        "source_name",
        "stage",
        "system_prompt",
        "domain_context",
        "input_contract",
        "output_contract",
        "corrections",
        "public_safety",
    },
    "CorpusSegment": {"segment_id", "source_id", "title", "source_type", "text", "citation"},
    "RagIndexRecord": {
        "object_type",
        "schema_version",
        "chunk_id",
        "segment_id",
        "source_id",
        "title",
        "source_type",
        "citation",
        "source_path",
        "source_url",
        "text",
        "collection",
        "domain",
        "content_hash",
        "embedding_model",
        "embedding_dimensions",
        "embedding_pooling",
        "artifact_pipeline",
        "public_safety_level",
        "embedding_status",
        "retrieval_metadata",
    },
    "RagIndex": {"object_type", "schema_version", "chunk_count", "embedding_status", "records"},
    "PublicSafetyReview": {"object_type", "schema_version", "status", "checked_records", "forbidden_pattern_hits", "rules"},
    "VectorExportRecord": {"object_type", "schema_version", "id", "embedding_text", "text", "metadata"},
    "EvidenceCitation": {"question", "rank", "segment_id", "source_id", "citation", "score", "excerpt"},
    "ReportBrief": {"object_type", "schema_version", "title", "questions", "evidence_citations"},
    "InformationObjectMap": {"object_type", "schema_version", "object_families", "pipelines"},
    "AnalysisMethodPack": {
        "object_type",
        "schema_version",
        "method_pack_version",
        "purpose",
        "object_families",
        "input_contracts",
        "output_contracts",
        "source_use_rules",
        "reporting_rules",
        "privacy_rules",
        "references",
    },
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require_fields(label: str, obj: dict[str, Any], fields: set[str], errors: list[str]) -> None:
    missing = sorted(field for field in fields if field not in obj)
    if missing:
        errors.append(f"{label}: missing {', '.join(missing)}")


def validate_schema_examples(root: Path, errors: list[str]) -> int:
    count = 0
    for path in sorted((root / "schemas").glob("*.json")):
        obj = load_json(path)
        object_type = obj.get("object_type")
        if not object_type:
            errors.append(f"{path}: missing object_type")
            continue
        fields = REQUIRED_FIELDS.get(object_type)
        if not fields:
            errors.append(f"{path}: unknown object_type {object_type}")
            continue
        require_fields(str(path), obj, fields, errors)
        count += 1
    return count


def validate_manifest(path: Path, errors: list[str]) -> int:
    manifest = load_json(path)
    records = manifest.get("sources", manifest.get("files", manifest.get("pages", [])))
    if not isinstance(records, list):
        errors.append(f"{path}: manifest records must be a list")
        return 0
    for idx, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"{path}: record {idx} is not an object")
            continue
        if "source_id" in record:
            require_fields(f"{path}: source {idx}", record, REQUIRED_FIELDS["SourceManifestRecord"], errors)
        elif "source_name" in record:
            require_fields(
                f"{path}: media source {idx}",
                record,
                {"source_name", "source_path", "download_status", "transcription_status", "cleanup_status", "corpus_status"},
                errors,
            )
        elif "page" in record:
            require_fields(f"{path}: page {idx}", record, {"page", "ocr_status", "cleanup_status"}, errors)
        else:
            errors.append(f"{path}: record {idx} has no recognized source identity")
    return len(records)


def validate_corpus(path: Path, errors: list[str]) -> int:
    corpus = load_json(path)
    segments = corpus.get("segments")
    if not isinstance(segments, list):
        errors.append(f"{path}: missing segments list")
        return 0
    for idx, segment in enumerate(segments, start=1):
        if not isinstance(segment, dict):
            errors.append(f"{path}: segment {idx} is not an object")
            continue
        require_fields(f"{path}: segment {idx}", segment, REQUIRED_FIELDS["CorpusSegment"], errors)
    expected_count = corpus.get("segment_count")
    if expected_count is not None and int(expected_count) != len(segments):
        errors.append(f"{path}: segment_count {expected_count} does not match {len(segments)} segments")
    return len(segments)


def validate_enrichment_packets(path: Path, errors: list[str]) -> int:
    if not path.exists():
        errors.append(f"{path}: missing enrichment packet directory")
        return 0
    count = 0
    for packet_path in sorted(path.glob("*.json")):
        packet = load_json(packet_path)
        require_fields(str(packet_path), packet, REQUIRED_FIELDS["TranscriptEnrichmentPacket"], errors)
        count += 1
    if count == 0:
        errors.append(f"{path}: no enrichment packets found")
    return count


def validate_report_brief(path: Path, errors: list[str]) -> int:
    brief = load_json(path)
    require_fields(str(path), brief, REQUIRED_FIELDS["ReportBrief"], errors)
    evidence = brief.get("evidence_citations", [])
    if not isinstance(evidence, list):
        errors.append(f"{path}: evidence_citations must be a list")
        return 0
    for idx, citation in enumerate(evidence, start=1):
        if not isinstance(citation, dict):
            errors.append(f"{path}: evidence citation {idx} is not an object")
            continue
        require_fields(f"{path}: evidence citation {idx}", citation, REQUIRED_FIELDS["EvidenceCitation"], errors)
    return len(evidence)


def validate_object_map(path: Path, errors: list[str]) -> int:
    object_map = load_json(path)
    require_fields(str(path), object_map, REQUIRED_FIELDS["InformationObjectMap"], errors)
    pipelines = object_map.get("pipelines", [])
    if not isinstance(pipelines, list):
        errors.append(f"{path}: pipelines must be a list")
        return 0
    for idx, pipeline in enumerate(pipelines, start=1):
        require_fields(
            f"{path}: pipeline {idx}",
            pipeline,
            {"pipeline", "source_manifest_records", "normalized_artifacts", "corpus_segments"},
            errors,
        )
    return len(pipelines)


def validate_method_pack(path: Path, errors: list[str]) -> int:
    pack = load_json(path)
    require_fields(str(path), pack, REQUIRED_FIELDS["AnalysisMethodPack"], errors)
    for field in ["object_families", "input_contracts", "output_contracts", "source_use_rules", "reporting_rules", "privacy_rules"]:
        if not isinstance(pack.get(field), list) or not pack.get(field):
            errors.append(f"{path}: {field} must be a non-empty list")
    if not isinstance(pack.get("references"), dict) or not pack.get("references"):
        errors.append(f"{path}: references must be a non-empty object")
    return 1


def validate_rag_index(path: Path, errors: list[str]) -> int:
    rag_index = load_json(path)
    require_fields(str(path), rag_index, REQUIRED_FIELDS["RagIndex"], errors)
    records = rag_index.get("records", [])
    if not isinstance(records, list):
        errors.append(f"{path}: records must be a list")
        return 0
    for idx, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"{path}: record {idx} is not an object")
            continue
        require_fields(f"{path}: record {idx}", record, REQUIRED_FIELDS["RagIndexRecord"], errors)
        if record.get("public_safety_level") != "L3_public_safe_derivative":
            errors.append(f"{path}: record {idx} must be L3 public-safe derivative")
        if record.get("domain") != "content_intelligence":
            errors.append(f"{path}: record {idx} must declare domain content_intelligence")
        if record.get("collection") not in {"evidence", "method"}:
            errors.append(f"{path}: record {idx} collection must be evidence or method")
        if record.get("embedding_pooling") != "cls":
            errors.append(f"{path}: record {idx} embedding_pooling must be cls")
        if Path(str(record.get("source_path", ""))).is_absolute():
            errors.append(f"{path}: record {idx} source_path must be repository-relative")
        if not str(record.get("source_url", "")).startswith(
            "https://github.com/grant-mccurdy/content-intelligence/blob/main/"
        ):
            errors.append(f"{path}: record {idx} source_url must link to the public repository")
    expected_count = rag_index.get("chunk_count")
    if expected_count is not None and int(expected_count) != len(records):
        errors.append(f"{path}: chunk_count {expected_count} does not match {len(records)} records")
    return len(records)


def validate_public_safety_review(path: Path, errors: list[str]) -> int:
    review = load_json(path)
    require_fields(str(path), review, REQUIRED_FIELDS["PublicSafetyReview"], errors)
    if review.get("status") != "pass":
        errors.append(f"{path}: public safety status is {review.get('status')}")
    hits = review.get("forbidden_pattern_hits", [])
    if not isinstance(hits, list):
        errors.append(f"{path}: forbidden_pattern_hits must be a list")
    elif hits:
        errors.append(f"{path}: forbidden pattern hits present")
    return 1


def validate_vector_records(path: Path, errors: list[str]) -> int:
    if not path.exists():
        errors.append(f"{path}: missing vector export")
        return 0
    count = 0
    with path.open(encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}: line {idx} invalid JSON: {exc.msg}")
                continue
            require_fields(f"{path}: line {idx}", record, REQUIRED_FIELDS["VectorExportRecord"], errors)
            metadata = record.get("metadata", {})
            if not isinstance(metadata, dict):
                errors.append(f"{path}: line {idx} metadata must be an object")
                continue
            if metadata.get("public_safety_level") != "L3_public_safe_derivative":
                errors.append(f"{path}: line {idx} must be L3 public-safe derivative")
            if metadata.get("domain") != "content_intelligence":
                errors.append(f"{path}: line {idx} must declare domain content_intelligence")
            if metadata.get("collection") not in {"evidence", "method"}:
                errors.append(f"{path}: line {idx} collection must be evidence or method")
            if not metadata.get("citation"):
                errors.append(f"{path}: line {idx} missing citation metadata")
            if metadata.get("embedding_model") != "@cf/baai/bge-base-en-v1.5":
                errors.append(f"{path}: line {idx} unexpected embedding model")
            if metadata.get("embedding_dimensions") != 768:
                errors.append(f"{path}: line {idx} unexpected embedding dimensions")
            if metadata.get("embedding_pooling") != "cls":
                errors.append(f"{path}: line {idx} embedding_pooling must be cls")
            fingerprint = str(metadata.get("corpus_fingerprint", ""))
            if len(fingerprint) != 64 or any(character not in "0123456789abcdef" for character in fingerprint):
                errors.append(f"{path}: line {idx} invalid corpus fingerprint")
            if not metadata.get("source_path") or not metadata.get("source_url"):
                errors.append(f"{path}: line {idx} missing direct source provenance")
            count += 1
    if count == 0:
        errors.append(f"{path}: no vector records found")
    return count


def validate(root: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    checked = 0
    checked += validate_schema_examples(root, errors)
    for path in [
        root / "data" / "processed" / "manifest.json",
        root / "sample_outputs" / "cloud_video_transcription" / "manifest.json",
        root / "sample_outputs" / "ocr_document_cleanup" / "manifest.json",
    ]:
        checked += validate_manifest(path, errors)
    for path in [
        root / "data" / "processed" / "corpus.json",
        root / "sample_outputs" / "cloud_video_transcription" / "corpus.json",
        root / "sample_outputs" / "ocr_document_cleanup" / "corpus.json",
    ]:
        checked += validate_corpus(path, errors)
    checked += validate_report_brief(root / "sample_outputs" / "report-brief.json", errors)
    checked += validate_enrichment_packets(root / "sample_outputs" / "cloud_video_transcription" / "enrichment_packets", errors)
    checked += validate_rag_index(root / "sample_outputs" / "rag-index.json", errors)
    checked += validate_public_safety_review(root / "sample_outputs" / "public-safety-review.json", errors)
    checked += validate_vector_records(root / "sample_outputs" / "vector-records.jsonl", errors)
    checked += validate_object_map(root / "sample_outputs" / "information-object-map.json", errors)
    checked += validate_method_pack(root / "method_pack" / "analysis-method-pack.json", errors)
    checked += validate_method_pack(root / "sample_outputs" / "analysis-method-pack.json", errors)
    return checked, errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated information objects.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checked, errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"validated {checked} objects with {len(errors)} errors", file=sys.stderr)
        return 1
    print(f"validated {checked} information objects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
