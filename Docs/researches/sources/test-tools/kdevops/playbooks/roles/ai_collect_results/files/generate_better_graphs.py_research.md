# sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_better_graphs.py

Purpose: Standalone AI benchmark graph generator focused on clearer QPS, latency, insert performance, and summary-table visuals.

Key APIs and flow: Filename helpers infer filesystem, node config, baseline/dev type, and iteration. `load_results()` enriches each `results_*.json` object. Chart functions aggregate query QPS and latency across top-k/batch combinations, compare baseline versus development bars, plot insert-rate distributions, and render a performance summary table image. `main()` loads results, creates the output directory, runs all charts, and prints counts.

State, dependencies, integration: Uses matplotlib Agg and writes `qps_comparison.png`, `latency_comparison.png`, `insert_performance.png`, and `performance_summary.png`. Depends on numpy and matplotlib; has a fallback `detect_filesystem()` that may SSH to `debian13-ai` but is not used by main flow.

Risks and test signals: Filename parsing is tailored to `debian13-ai-*`; best-query summary uses maxima rather than matched configurations; random jitter makes scatter placement nondeterministic. Tests should cover dev/baseline filename variants, missing query data, and no comparison pairs.
