## sources/test-tools/kdevops/workflows/minio/scripts/generate_warp_report.py

Purpose: Generates per-result MinIO Warp throughput/operation graphs and an HTML report.

Important APIs/types/functions: Functions are `parse_warp_json`, `generate_throughput_graph`, `generate_operation_stats_graph`, `generate_html_report`, and `main`.

Control flow: `main` accepts an optional results directory, finds `warp_benchmark_*.json`, builds an HTML report over all results, then separately generates graphs for the most recent result. Parsing skips any non-JSON prefix before the first `{`.

State and persistence: Reads warp JSON files and writes `warp_benchmark_report.html` plus `*_throughput.png` and `*_operations.png` chart files in the results directory.

Dependencies and integration points: Called by `make minio-results`. Requires matplotlib and a Warp JSON schema with `total.throughput.segmented.segments` for throughput graphs.

Risks and test signals: The timestamp parser replaces only `-07:00`, which is brittle for other offsets, and the CSS contains an extra brace. Test with JSON from multiple time zones and confirm HTML/charts render.
