<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread.py

## Purpose
Measures single-thread read bandwidth through a GCSFuse mount after ensuring fixed-size test objects exist in the target bucket.

## Important APIs, Types, And Functions
`check_and_create_files`, `read_all_files`, and CLI `main`. Constants define mount directory `gcs` and `testfile_read` prefix.

## Control Flow
Main mounts the bucket, uses the Cloud Storage client to create or repair missing test files with `fallocate` and upload, reads all expected files through the mount, unmounts, logs throughput to BigQuery, and checks a 160 MB/s threshold.

## State And Persistence Behavior
Creates temporary `/tmp` files, uploads GCS objects, reads from the FUSE mount, removes local temp files, writes BigQuery rows, and exits nonzero on read or threshold failures.

## Dependencies
Uses `google-cloud-storage`, local `helper`, `fallocate`, GCSFuse, and filesystem IO.

## Integration Points
Called by `run_microbenchmark.sh` with a production bucket, 10 files, and 15GB file size by default.

## Risks And Edge Cases
Reads entire files into memory with `f.read()`, so large defaults can stress RAM. Mount failure return is not checked before continuing. Object names are deterministic and shared across runs.

## Test Signals
Tests cover byte counting, read errors, missing/undersized/exact-size object handling, upload failure cleanup, and temp file removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread.py -->
