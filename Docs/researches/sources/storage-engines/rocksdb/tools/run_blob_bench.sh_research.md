# sources/storage-engines/rocksdb/tools/run_blob_bench.sh

## Purpose
This Bash script runs a predefined BlobDB benchmark sequence through `tools/benchmark.sh`. It covers write-only, read-write, and read-only phases with blob-file and blob-cache options exposed through environment variables.

## Important APIs, Types, and Functions
`display_usage` documents required paths and tunables. The script validates `DB_DIR`, `WAL_DIR`, `OUTPUT_DIR`, and the presence of `tools/benchmark.sh`. It computes size defaults, blob options, target SST file size, and level-base size, then builds `ENV_VARS`, `ENV_VARS_D`, `PARAMS`, and `PARAMS_GC` strings passed to benchmark invocations.

## Control Flow
After argument and environment validation, it prints the benchmark setup, removes old DB/WAL/output directories, and runs six benchmark phases: `bulkload`, `overwrite`, `readwhilewriting`, `fwdrangewhilewriting`, `readrandom`, and `fwdrange`. It copies RocksDB `LOG*` files into the output directory at the end.

## State and Persistence
It destructively recreates the DB, WAL, and output directories. Benchmark results and copied logs persist in `OUTPUT_DIR`. No checkpointing or resume behavior is implemented.

## Dependencies and Integration Points
It depends on Bash, `env -S`, `rm`, `cp`, and `tools/benchmark.sh`, which in turn drives `db_bench`. It integrates with BlobDB options such as blob file size, blob GC thresholds, blob cache settings, and starting level.

## Risks
`rm -rf` is run on environment-provided directories after only non-empty validation. `env -S` is not portable to all Unix environments. Option strings are assembled as shell words and can break with spaces. The derived `target_file_size_base` formula changes dramatically when blob files are enabled and should be understood before comparing runs.

## Test Signals
Successful completion leaves benchmark logs and a `report.tsv`/benchmark output from `benchmark.sh`, plus RocksDB LOG files copied into `OUTPUT_DIR`.
