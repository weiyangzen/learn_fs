# sources/storage-engines/rocksdb/tools/benchmark_compare.sh

## Purpose

This script compares performance across one or more RocksDB `db_bench.<version>` binaries by running a fixed benchmark sequence and generating per-version reports plus a cross-version summary.

## Important APIs, Types, and Functions

It accepts `db_dir output_dir version+`, collects environment knobs for benchmark shape and RocksDB options, builds arrays `base_args`, `args_common`, `args_load`, `args_nolim`, and `args_lim`, and defines `usage` and `dump_env`.

## Control Flow

After validation, it loops over each version, creates a version output directory, symlinks `db_bench` to `db_bench.<version>`, clears database files, runs load, read-only, read-mostly, and write-only jobs through `benchmark.sh`, copies/gzips LOG files, then builds `summary.tsv` by grouping corresponding report rows across versions.

## State and Persistence Behavior

It creates output directories, args files, symlinks, reports, summary TSV, RocksDB database contents, and compressed logs. It deletes files under `dbdir` between versions.

## Dependencies and Integration Points

It depends on Bash arrays, `benchmark.sh`, versioned db_bench binaries, coreutils, gzip, and `awk`. `benchmark_ci.py` calls it for a single current version.

## Risks and Test Signals

Risks include destructive `find "$dbdir" -type f -exec rm`, symlink replacement, output directory refusal if preexisting, unquoted conditionals in places, and variability from compaction debt. Signals are per-version `report.tsv`, copied/gzipped LOG files, `args`, and final `summary.tsv` grouping.
