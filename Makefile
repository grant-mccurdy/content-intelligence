.PHONY: all demo manifest corpus report search media-demo ocr-demo rag-index vector-export object-map method-pack validate portfolio-demo clean

PYTHON ?= python3
QUERY ?= source grounded report citations

all: portfolio-demo

demo: manifest corpus report

manifest:
	$(PYTHON) scripts/build_manifest.py

corpus: manifest
	$(PYTHON) scripts/build_corpus.py

report: corpus
	$(PYTHON) scripts/generate_report.py

search: corpus
	$(PYTHON) scripts/search_corpus.py "$(QUERY)"

media-demo:
	$(PYTHON) demos/cloud_video_transcription/run_demo.py

ocr-demo:
	$(PYTHON) demos/ocr_document_cleanup/run_demo.py

rag-index: report media-demo ocr-demo
	$(PYTHON) scripts/build_rag_index.py

vector-export: rag-index
	$(PYTHON) scripts/export_vector_records.py

object-map: report media-demo ocr-demo rag-index vector-export
	$(PYTHON) scripts/build_information_object_map.py

method-pack: object-map
	$(PYTHON) scripts/build_analysis_method_pack.py

validate:
	$(PYTHON) scripts/validate_information_objects.py

portfolio-demo: demo media-demo ocr-demo rag-index vector-export object-map method-pack validate

clean:
	rm -rf data/processed sample_outputs/demo-report.md sample_outputs/report-brief.json sample_outputs/information-object-map.json sample_outputs/analysis-method-pack.json sample_outputs/rag-index.json sample_outputs/public-safety-review.json sample_outputs/vector-records.jsonl sample_outputs/cloud_video_transcription sample_outputs/ocr_document_cleanup
