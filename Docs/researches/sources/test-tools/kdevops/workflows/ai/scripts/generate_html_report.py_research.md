# sources/test-tools/kdevops/workflows/ai/scripts/generate_html_report.py

## Purpose
Builds an HTML report for AI/Milvus benchmark results by combining graph summary data, detailed result JSON, and relative graph image references.

## Important APIs, Types, and Functions
Important functions are `load_summary()`, `load_results()`, `generate_table_rows()`, `generate_config_summary()`, `find_performance_trend_graphs()`, `generate_html_report()`, and `main()`. Result rows are dictionaries with host, filesystem, block size, baseline/dev type, insert/query QPS, timestamp, and dev flag.

## Control Flow
The CLI expects `<results_dir> <graphs_dir> <output_html>`. It loads `summary.json` or creates a fallback, parses detailed JSON files, switches sections based on whether more than one filesystem was tested, formats `HTML_TEMPLATE`, and writes the output HTML.

## State and Persistence Behavior
The script writes one HTML file and does not copy graph assets; relative `graphs/*.png` paths must exist where the report is served.

## Dependencies and Integration Points
Uses only Python standard-library modules. Integrates with AI benchmark result JSON and graph outputs from `generate_graphs.py`.

## Risks and Edge Cases
Unescaped JSON/filename values are injected into HTML. The detailed table header has six columns while generated rows have seven cells. Best-config highlighting depends on matching independently generated config key strings.

## Test Signals
Test missing summary, single and multi-filesystem summaries, absent graph files, incomplete result JSON, and filename patterns for XFS/ext4/btrfs/dev/baseline. Validate HTML table structure.
