# sources/storage-engines/wiredtiger/bench/perf_run_py/perf_stat_collection.py

## Purpose
This module declares the catalog of supported performance metric labels and coordinates extraction of requested stats from test home directories.

## Important APIs, Types, and Functions
`create_test_stat_path` joins a home path and stat filename. `PerfStatCollection.__init__` filters `all_stats()` by requested operation short labels. `find_stats` searches each candidate stat file and adds values. Static methods `cache_eviction_stats`, `latency_stats`, and `all_stats` define the supported metrics.

## Control Flow
Callers construct a collection with operation names, run tests, then call `find_stats` for each home. For each configured stat, it searches its ordered `stat_files`; if two files match for one metric, it raises a runtime error, otherwise it appends found values to the metric.

## State, Persistence, and Dependencies
State is `to_report`, a list of `PerfStat` instances that accumulate values across runs. Dependencies are local stat classes and output files such as `test.stat`, `workload.stat`, `latency.stat`, `monitor.json`, `cache_eviction.stat`, `prefetch_stats.out`, `WiredTigerStat*`, and `stdout_file.txt`.

## Integration Points, Risks, and Test Signals
This is the central stat registry used by `validate_operations` and `process_results`. Risks include regex/input-offset coupling to exact stat text, duplicate short labels not being guarded except by caller validation, and empty requested operations producing no metrics. Signal is a non-empty `to_report` with populated values.
