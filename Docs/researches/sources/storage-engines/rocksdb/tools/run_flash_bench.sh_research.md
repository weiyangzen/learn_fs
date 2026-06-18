# sources/storage-engines/rocksdb/tools/run_flash_bench.sh

## Purpose
This Bash script runs a broad flash-storage benchmark sequence with RocksDB `tools/benchmark.sh`. It prepares or restores a database, runs setup writes, read-only tests, read-write tests, merge tests, and a universal compaction test, then builds summarized reports.

## Important APIs, Types, and Functions
The script is top-level imperative Bash. It defines size constants and tunables from environment variables such as `NKEYS`, write rate limits, duration, range length, value size, block/cache sizes, data/WAL dirs, setup/save flags, and `SKIP_LOW_PRI_TESTS`. It builds an `ARGS` environment string and repeatedly invokes `./tools/benchmark.sh`.

## Control Flow
It chooses requested thread counts from command-line arguments or defaults to 24. In setup mode it may run `bulkload`, large and normal `fillseq` with WAL disabled/enabled, and single-threaded overwrite. Restore mode copies `.bak` directories back into place. It optionally saves setup backups, then loops over thread counts for readrandom/range scans, overwrite/update/readwhilewriting/rangewhilewriting, merge workloads, and universal compaction. Finally it greps `report.txt` into `report2.txt`.

## State and Persistence
The script writes benchmark output under `${TMPDIR:-/tmp}/output`, creates/modifies `DATA_DIR` and `LOG_DIR`, and can copy persistent `.bak` snapshots. It deletes and restores directories with `rm -rf` and `cp -p -r`.

## Dependencies and Integration Points
It depends on `tools/benchmark.sh`, shell utilities, and RocksDB `db_bench` behavior through benchmark wrappers. Report construction assumes the format emitted by `benchmark.sh`.

## Risks
Environment-provided paths are removed without robust safety guards. Some summary lines duplicate redirects, for example `echo readwhile >> $output_dir/report2.txt >> $output_dir/report2.txt`. Grep patterns are brittle and can fail if test names change. Long default durations and key counts can be expensive. No `set -e` means intermediate failures may not stop the script unless `benchmark.sh` handles them.

## Test Signals
Successful runs produce `report.txt`, `report2.txt`, and per-test output logs. Comparing report rows across runs is the primary regression signal.
