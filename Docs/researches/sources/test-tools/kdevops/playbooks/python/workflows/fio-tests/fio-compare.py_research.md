# sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-compare.py

Purpose: Compares fio JSON result directories for baseline versus development configurations and emits PNG charts plus a text summary.

Key APIs and flow: `parse_fio_json()` extracts first-job read/write bandwidth, IOPS, and mean latency from fio JSON. `extract_test_params()` decodes block size, IO depth, job count, and pattern from `results_*.json` filenames. `load_results()` builds pandas DataFrames per config. Plotters create side-by-side bars and percentage delta charts, while `generate_summary_report()` writes average metric changes.

State, dependencies, integration: Reads only local result files, creates an output directory, writes PNGs and `<prefix>_summary.txt`. Depends on pandas and matplotlib. Intended for fio workflow A/B analysis.

Risks and test signals: Only the first fio job is used; text-result fallback is discovered but skipped; filename parsing can omit required columns and break groupbys; latency improvement direction differs from throughput. Tests should use minimal fio JSON fixtures, mismatched config sets, zero baselines, malformed filenames, and missing directories.
