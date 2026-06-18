# sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-plot.py

Purpose: Creates a compact set of fio performance plots for one result directory: bandwidth heatmap, IOPS scaling, latency distribution, and pattern comparison.

Key APIs and flow: `create_performance_matrix()` loads `results_*.json`, uses `parse_fio_json()` for first-job metrics, and merges filename-derived parameters from `extract_test_params()`. Plot helpers guard against missing columns and save prefixed PNGs. `main()` validates inputs, creates output directory, exits on no valid results, and invokes all plotters.

State, dependencies, integration: The script is stateless beyond generated PNG files. It uses pandas and matplotlib and expects kdevops fio result filenames with `bs`, `iodepth`, `jobs`, and workload pattern tokens.

Risks and test signals: Text fallback is intentionally skipped; malformed numeric tokens raise `ValueError`; missing pattern data suppresses some plots; only mean latency is considered. Tests should include read-only, write-only, mixed, missing-latency, malformed filename, and empty-directory fixtures.
