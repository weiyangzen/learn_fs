# sources/storage-engines/rocksdb/tools/benchmark_leveldb.sh

## Purpose

This legacy wrapper runs LevelDB fork benchmarks using a db_bench-compatible binary and emits a small report for comparison with RocksDB-style workloads.

## Important APIs, Types, and Functions

It accepts one comma-separated job argument among `fillseq`, `overwrite`, `readrandom`, `readwhilewriting`, and `debug`. Environment knobs include `DB_DIR`, `OUTPUT_DIR`, `DB_BENCH_NO_SYNC`, `NUM_THREADS`, `WRITES_PER_SECOND`, `CACHE_SIZE`, `NUM_KEYS`, and `VALUE_SIZE`. Functions include `summarize_result`, `run_fillseq`, `run_change`, `run_readrandom`, `run_readwhile`, and `now`.

## Control Flow

The script validates a single argument and `DB_DIR`, builds common db_bench flags, dispatches jobs, logs schedule entries, executes commands through `eval`/`tee`, parses output metrics, appends `report.txt`, and prints the latest row.

## State and Persistence Behavior

It writes logs, `report.txt`, and `schedule.txt` under `OUTPUT_DIR`, and mutates the database under `DB_DIR`.

## Dependencies and Integration Points

It depends on a LevelDB fork's `db_bench` binary with expected options and output format, plus shell utilities and `bc`.

## Risks and Test Signals

Risks include legacy output parsing, no support for many modern RocksDB settings, unquoted variables, and `eval`. Signals are benchmark logs, report rows with ops/sec/latency, and schedule timing.
