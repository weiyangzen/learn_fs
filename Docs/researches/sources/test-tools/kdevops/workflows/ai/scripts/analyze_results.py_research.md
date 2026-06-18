# sources/test-tools/kdevops/workflows/ai/scripts/analyze_results.py

Purpose: AI benchmark post-processing tool. It loads `results_*.json` files, summarizes Milvus vector insert/index/query performance, captures local DUT information, writes text/HTML/consolidated JSON reports, and optionally generates matplotlib/seaborn graphs.

The main type is `ResultsAnalyzer`. Important methods include `_collect_system_info()`, `_get_storage_info()`, `_get_nvme_info()`, `_detect_virtualization()`, `_get_filesystem_info()`, `_extract_filesystem_config()`, `_extract_node_info()`, `load_results()`, `generate_summary_report()`, `generate_html_report()`, `generate_graphs()`, plotting helpers for insert/query/index/matrix/filesystem comparison, and `analyze()`. CLI requires `--results-dir` and `--output-dir`, with optional JSON `--config`.

Control flow loads optional graph libraries at import time, creates the output directory, reads all result JSON files, writes `benchmark_summary.txt`, `benchmark_report.html`, optional PNGs, and `consolidated_results.json`. Multi-node baseline/dev comparisons are inferred from hostnames ending in `-dev`; filesystem/block-size labels are primarily inferred from filenames.

State includes result files, local `/proc`, `lsblk`, `nvme`, `df`, `dmesg`, output reports, and graph files. Risks include unescaped HTML from result data, broad bare `except`, filename heuristics overriding JSON, missing graph libraries causing summary-only output, and local analyzer host info being mixed with DUT result info. Tests should use fixture JSONs for single-node and baseline/dev cases, mock subprocesses, validate generated reports, and exercise graph-disabled and graph-missing paths.
