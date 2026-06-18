# sources/storage-engines/rocksdb/tools/benchmark_ci.py

## Purpose

This Python wrapper runs `benchmark_compare.sh` for the current RocksDB build/version in CI, using the just-built `db_bench` binary and copying the resulting report to a stable output path.

## Important APIs, Types, and Functions

`Config` stores version, data, result, script, and cwd paths plus `benchmark_env_keys`. Functions are `read_version`, `prepare`, `results`, `cleanup`, `get_benchmark_env`, and `main`.

## Control Flow

`main` parses directories and key count, reads `include/rocksdb/version.h`, builds a version string, removes stale result contents for that version, symlinks `tools/db_bench.<version>` to the current `db_bench`, collects allowed environment variables, runs `benchmark_compare.sh db_dir results_dir version`, copies `<version>/report.tsv` to `results_dir/report.tsv`, and removes the symlink in `finally`.

## State and Persistence Behavior

It deletes old files/directories under the versioned results directory, creates/removes a symlink in `tools`, and writes/copies benchmark reports.

## Dependencies and Integration Points

It depends on Python stdlib, RocksDB version headers, built `db_bench`, and `tools/benchmark_compare.sh`.

## Risks and Test Signals

Risks include recursive cleanup with plain `os.rmdir`, symlink collisions, no `check=True` on `subprocess.run`, and environment truncation to whitelisted keys. Signals are logged version, successful symlink lifecycle, benchmark_compare output, and copied `report.tsv`.
