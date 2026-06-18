# sources/storage-engines/wiredtiger/bench/perf_run_py/aggregate_perf_stat.py

## Purpose
This script aggregates multiple Evergreen-style performance JSON files into a simple CSV named `all_stats.csv`.

## Important APIs, Types, and Functions
`main` uses `glob.glob('perf_stats/*.json')`, `json.load`, and writes columns `Test Name, Metric Name, Value`.

## Control Flow, State, and Dependencies
The script opens `all_stats.csv`, iterates every JSON file under `perf_stats`, expects each file to contain a list with a first element having `info.test_name` and `metrics`, and writes one CSV row per metric. State is the output CSV file.

## Integration Points, Risks, and Test Signals
It integrates with `perf_run.py` brief output or similar Evergreen-compatible files. Risks include no CSV escaping for metric names containing commas, no context manager for the output file, and failure on detailed Atlas-style JSON. Signal is a populated `all_stats.csv`.
