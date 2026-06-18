# sources/storage-engines/rocksdb/tools/benchmark.sh

## Purpose

`benchmark.sh` is the main RocksDB performance benchmark wrapper around `db_bench`. It provides named benchmark jobs, environment-driven configuration, stats collection, and normalized TSV reporting.

## Important APIs, Types, and Functions

It defines many environment knobs: DB/WAL/output paths, key/value sizes, cache, compression, compaction style, blob settings, O_DIRECT, sync, threads, durations, and write limits. Important functions are `display_usage`, `get_cmd`, `start_stats`, `stop_stats`, `units_as_gb`, `summarize_result`, `run_bulkload`, `run_manual_compaction_worker`, `run_univ_compaction`, `run_fillseq`, `run_lsm`, `run_change`, `run_filluniquerandom`, read/range helpers, and `run_randomtransaction`.

## Control Flow

The script validates arguments and required `./db_bench`, builds common db_bench argument strings based on compaction style, dispatches comma-separated jobs, records schedule start/end entries, runs db_bench under `/usr/bin/time` and optional `timeout`/`numactl`, starts background `iostat`, `vmstat`, process, and size samplers for most jobs, summarizes db_bench output, and appends one TSV report row per benchmark.

## State and Persistence Behavior

It creates output logs, `.time`, `.stats.*`, compressed iostat/vmstat files, `schedule.txt`, and `report.tsv`. It mutates the RocksDB database and WAL directories according to each benchmark.

## Dependencies and Integration Points

It depends on `db_bench`, Bash, GNU-ish core utilities, `awk`, `bc`, `gzip`, `iostat`, `vmstat`, `ps`, and RocksDB db_bench output formats. `benchmark_compare.sh` and CI wrappers call it.

## Risks and Test Signals

Risks include unquoted variables, `eval`, fragile grep/awk parsing, background process cleanup via broad `killall`, output format drift, and destructive DB reuse. Signals are completed jobs, report header/rows, schedule entries, compressed stats files, and nonfailed TSV metrics.
