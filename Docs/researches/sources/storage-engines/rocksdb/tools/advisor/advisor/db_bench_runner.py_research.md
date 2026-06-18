# sources/storage-engines/rocksdb/tools/advisor/advisor/db_bench_runner.py

## Purpose

`db_bench_runner.py` implements the Advisor `BenchmarkRunner` contract for RocksDB's `db_bench`. It prepares a database, executes one benchmark, parses throughput and perf context output, and returns Advisor data sources for rules.

## Important APIs, Types, and Functions

`DBBenchRunner` defines `OUTPUT_FILE`, `ERROR_FILE`, `DB_PATH`, `THROUGHPUT`, and `PERF_CON`. Key methods are `is_metric_better`, `get_opt_args_str`, `_parse_output`, `get_log_options`, `_get_options_command_line_args_str`, `_setup_db_before_experiment`, `_build_experiment_command`, `_run_command`, and `run_experiment`.

## Control Flow

Construction stores the `db_bench` binary, benchmark name, optional db_bench args, and optional ODS args. `run_experiment` removes/reloads the DB with `fillrandom`, builds the benchmark command with `--statistics --perf_level=3`, records start/end time, runs it through `subprocess.call(shell=True)`, parses output, constructs `DatabaseLogs`, `LogStatsParser`, `DatabasePerfContext`, and optional `OdsStatsFetcher`, then returns data sources and throughput.

## State and Persistence Behavior

It overwrites `temp/dbbench_out.tmp` and `temp/dbbench_err.tmp`, removes the target DB path before setup, generates temporary OPTIONS files, and reads RocksDB LOG files. Perf context is converted into a timestamped in-memory time series.

## Dependencies and Integration Points

It depends on `shutil`, `subprocess`, `time`, `BenchmarkRunner`, `DatabaseOptions`, log/stat fetchers, and the external `db_bench` binary.

## Risks and Test Signals

Risks include shell command injection through option strings, fixed temp filenames, non-thread-safety, assumptions about `db_bench` output format, and destructive DB path cleanup. Tests cover setup, log filename/path selection, optional argument string construction, experiment command building, and a live experiment when `db_bench` is available.
