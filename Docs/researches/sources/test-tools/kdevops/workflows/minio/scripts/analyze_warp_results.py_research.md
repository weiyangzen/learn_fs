## sources/test-tools/kdevops/workflows/minio/scripts/analyze_warp_results.py

Purpose: Loads MinIO Warp JSON results, extracts performance metrics, and generates charts plus text/HTML reports.

Important APIs/types/functions: Functions include `load_warp_results`, `extract_metrics`, `generate_throughput_chart`, `generate_latency_chart`, `generate_performance_summary_chart`, `generate_text_report`, `generate_html_report`, and `main`.

Control flow: `main` resolves `workflows/minio/results`, loads `warp_benchmark_*.json`, extracts metrics from `total`, `by_op_type`, and `summary` structures, then writes throughput, latency, summary PNGs, a text report, and an HTML dashboard.

State and persistence: Reads result JSON files and writes `warp_throughput_performance.png`, `warp_latency_analysis.png`, `warp_performance_summary.png`, `warp_analysis_report.txt`, and `warp_benchmark_report.html`.

Dependencies and integration points: Requires Python, matplotlib, numpy, and optionally dateutil for robust timestamp parsing. It is a standalone analyzer adjacent to the MinIO workflow results directory.

Risks and test signals: Some report fields use metric keys that `extract_metrics` does not populate (`latency_min_ms`, `ops_total`, `error_rate`), so tables can show zeros despite available data. Test with representative Warp JSON schemas and verify generated charts are meaningful.
