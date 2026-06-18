# sources/test-tools/kdevops/workflows/ai/scripts/generate_graphs.py

## Purpose
Generates PNG graphs for Milvus AI benchmark JSON results: insert performance trends and query heatmaps. It reads `results_*.json`, annotates loaded dicts with `_file`, infers filesystem/node metadata, and writes graph images to an output directory.

## Important APIs, Types, and Functions
Key functions are `_extract_filesystem_config()`, `_extract_node_info()`, `load_results()`, `create_simple_performance_trends()`, `create_heatmap_analysis()`, and `main()`. It uses plain dictionaries, `defaultdict`, numpy matrices, and matplotlib with the `Agg` backend.

## Control Flow
`main()` validates `<results_dir> <output_dir>`, loads result JSON, then calls the two graph builders. Filesystem parsing prefers filename substrings and falls back to JSON; heatmap generation groups query QPS by fixed top-k and batch keys.

## State and Persistence Behavior
No durable state is kept besides output PNG files. Inputs are read-only JSON files; output files include `performance_trends.png` and `performance_heatmap.png`.

## Dependencies and Integration Points
Depends on numpy/matplotlib and the AI benchmark result schema. `generate_html_report.py` expects these graph paths under `graphs/`.

## Risks and Edge Cases
`create_simple_performance_trends()` uses undefined `fs_performance` after initializing `node_performance`, so trend generation can fail. Filename parsing is fragile, and missing heatmap cells are silently rendered as zero.

## Test Signals
Run against empty, single-result, multi-filesystem, malformed, and missing-key result directories. Assert both PNGs are non-empty and that trend generation no longer raises `NameError`.
