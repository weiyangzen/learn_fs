# sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-trend-analysis.py

Purpose: Performs deeper fio trend analysis across block size, IO depth, latency percentiles, and metric correlations.

Key APIs and flow: `parse_fio_json()` extracts read/write bandwidth, IOPS, mean/stddev/p95/p99 latency, and totals from the first fio job. `extract_test_params()` turns filename tokens into numeric block size, IO depth, job count, and pattern. `load_all_results()` returns a DataFrame, then plotting functions save `block_size_trends.png`, `io_depth_scaling.png`, `latency_percentiles.png`, and `correlation_heatmap.png`.

State, dependencies, integration: Reads local `results_*.json`, writes fixed output files, and depends on pandas, matplotlib, seaborn, and numpy. It is a post-processing tool for fio test sweeps.

Risks and test signals: Block-size parsing supports only bare numbers and `k`; text results are skipped; correlation assumes all numeric columns exist; zero latency values are filtered. Tests should exercise missing percentile fields, non-k block sizes, partial pattern sets, and one-row correlations.
