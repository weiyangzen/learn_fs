<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread.py

## Purpose
Measures single-thread write bandwidth through a GCSFuse mount by writing deterministic numbers of random binary files.

## Important APIs, Types, And Functions
`delete_existing_file`, `write_random_file`, `create_files`, and CLI `main`. Constants define mount directory `gcs` and object prefix `testfile`.

## Control Flow
Main mounts the bucket, builds target paths, deletes existing objects through the mount, writes random bytes with `os.urandom`, unmounts, logs throughput to BigQuery, and checks an 80 MB/s historical threshold.

## State And Persistence Behavior
Creates/removes files on the mounted bucket, writes BigQuery rows, and may exit the process on delete/write/threshold failures.

## Dependencies
Uses local `helper`, GCSFuse, Python filesystem APIs, and BigQuery through helper.

## Integration Points
Called by `run_microbenchmark.sh` with one 15GB file by default.

## Risks And Edge Cases
`os.urandom(file_size)` materializes the entire file payload in memory, which is risky for 15GB writes. Mount failures are not checked before writes, and `create_files` can return `None` only for some exception paths.

## Test Signals
Tests cover delete behavior, random file writes, aggregate byte count, and failure exit when write fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread.py -->
