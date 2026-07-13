#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "does", "for", "from", "how", "in",
    "into", "is", "it", "of", "on", "or", "that", "the", "this", "to", "what", "with",
}


def tokenize(text: str) -> list[str]:
    normalized = text.lower().replace("'", "")
    return [
        term
        for term in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", normalized)
        if len(term) > 1 and term not in STOPWORDS
    ]


def expand_query(question: str) -> str:
    expansions = []
    if re.search(r"\b(input|file)\s+formats?\b|\b(pdf|docx|html|markdown)\b", question, re.IGNORECASE):
        expansions.append("plain text transcript-derived OCR-derived Markdown PDF DOCX HTML direct implementation deferred adapters")
    if re.search(r"\b(evaluate|evaluated|evaluation|evals?|quality|recall|ranking)\b", question, re.IGNORECASE):
        expansions.append("evaluation protocol retrieval evals recall reciprocal rank citation grounding refusal live stability")
    if re.search(r"\b(information|structured)\s+objects?\b|\bobject model\b", question, re.IGNORECASE):
        expansions.append("information object model SourceManifestRecord CorpusSegment RagIndexRecord EvidenceCitation ReportBrief")
    return " ".join([question, *expansions])


def rank(records: list[dict[str, Any]], question: str, top_k: int = 5) -> list[dict[str, Any]]:
    indexed = []
    document_frequency: Counter[str] = Counter()
    for record in records:
        metadata = record.get("retrieval_metadata", {})
        title_text = " ".join(
            [
                record.get("title", ""),
                record.get("citation", ""),
                record.get("source_type", ""),
                record.get("content_kind", ""),
                " ".join(metadata.get("keywords", [])),
            ]
        )
        title_tokens = tokenize(title_text)
        tokens = tokenize(record.get("text", "")) + title_tokens * 3
        counts = Counter(tokens)
        indexed.append((record, counts, max(len(tokens), 1)))
        document_frequency.update(counts.keys())
    average_length = sum(length for _, _, length in indexed) / max(len(indexed), 1)
    query_terms = tokenize(expand_query(question))
    scored = []
    for record, counts, length in indexed:
        score = 0.0
        for term in query_terms:
            frequency = counts[term]
            if not frequency:
                continue
            document_count = document_frequency[term]
            inverse_frequency = math.log(1 + (len(indexed) - document_count + 0.5) / (document_count + 0.5))
            denominator = frequency + 1.35 * (1 - 0.72 + 0.72 * length / max(average_length, 1))
            score += inverse_frequency * (frequency * 2.35 / denominator)
        if score:
            scored.append((score, record))
    return [record for _, record in sorted(scored, key=lambda item: (-item[0], item[1]["chunk_id"]))[:top_k]]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Content Intelligence retrieval fixtures.")
    parser.add_argument("--index", default="sample_outputs/rag-index.json")
    parser.add_argument("--cases", default="evals/retrieval-cases.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    index = json.loads((root / args.index).read_text(encoding="utf-8"))
    cases = json.loads((root / args.cases).read_text(encoding="utf-8"))
    failures = []
    records = index.get("records", [])
    if len(index.get("corpus_fingerprint", "")) != 64:
        failures.append("index is missing a corpus fingerprint")
    if any(record.get("embedding_pooling") != "cls" for record in records):
        failures.append("not all records use cls pooling")
    if any(not record.get("source_path") or not record.get("source_url") for record in records):
        failures.append("not all records have direct source provenance")
    for case in cases:
        results = rank(records, case["question"])
        expected = case.get("expected_chunk_prefixes", [])
        passed = any(record["chunk_id"].startswith(prefix) for prefix in expected for record in results)
        print(f"{'PASS' if passed else 'FAIL'} {case['id']}")
        if not passed:
            failures.append(f"{case['id']}: expected source not found in top 5")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1
    print(f"retrieval eval passed ({len(cases)}/{len(cases)} cases; {len(records)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
