# sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_graphs.py

Purpose: Older/simple AI benchmark graph generator for insert trends and query-performance heatmaps.

Key APIs and flow: `_extract_filesystem_config()` and `_extract_node_info()` infer grouping from filenames or result `system_info`. `load_results()` reads `results_*.json`. `create_heatmap_analysis()` groups query QPS by filesystem config and writes `performance_heatmap.png`. `create_simple_performance_trends()` appears intended to group insert rates/times and write `performance_trends.png`.

State, dependencies, integration: Uses matplotlib Agg, numpy, and JSON result files; writes graphs to the provided output directory. It is copied by `ai_collect_results`, though comments now indicate graph generation is handled by `analyze_results.py`.

Risks and test signals: `create_simple_performance_trends()` references `fs_performance` without defining it after initializing `node_performance`, causing a `NameError` when insert data exists. The `Path` and `datetime` imports are unused. Tests should call both graph functions with minimal result fixtures and catch this regression.
