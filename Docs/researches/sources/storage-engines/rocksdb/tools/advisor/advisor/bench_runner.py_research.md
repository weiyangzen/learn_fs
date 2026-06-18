# sources/storage-engines/rocksdb/tools/advisor/advisor/bench_runner.py

## Purpose

`bench_runner.py` defines the abstract benchmark-runner contract used by the Advisor optimizer. It lets the optimizer compare experiment metrics and request data sources without knowing the benchmark backend.

## Important APIs, Types, and Functions

`BenchmarkRunner` is an `ABC` with abstract `is_metric_better(new_metric, old_metric)` and `run_experiment()`. The concrete helper `get_info_log_file_name(log_dir, db_path)` reproduces RocksDB info-log prefix naming when `db_log_dir` redirects logs away from the database path.

## Control Flow

Subclasses implement execution and metric comparison. The static log-name helper strips the leading slash from `db_path`, replaces non `[0-9a-zA-Z-_\.]` characters with underscores, appends a trailing underscore when needed, and finally appends `LOG`; if no log directory is configured, it returns `LOG`.

## State and Persistence Behavior

The base class has no instance state. The helper computes names for persisted RocksDB LOG files but does not access the filesystem.

## Dependencies and Integration Points

It depends on `abc` and `re`. `DBBenchRunner` subclasses it, and tests assert the log filename contract used by RocksDB's `GetInfoLogPrefix()`.

## Risks and Test Signals

Risks are mismatch with RocksDB's real log naming rules and the abstract `run_experiment` signature differing from subclass arguments. Signals include `test_get_info_log_file_name`, successful subclass instantiation, and optimizer operation against redirected log directories.
