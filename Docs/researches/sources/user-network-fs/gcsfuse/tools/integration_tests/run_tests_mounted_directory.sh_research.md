# sources/user-network-fs/gcsfuse/tools/integration_tests/run_tests_mounted_directory.sh

## Purpose

This script runs a broad integration-test matrix against an already provided mount directory. It repeatedly mounts and unmounts a supplied bucket with different GCSFuse flags, then invokes targeted `go test` packages with `--mountedDirectory` and `--testbucket`.

## Important APIs, Types, and Functions

Inputs are test bucket, mount directory, and optional zonal flag. It exports `CGO_ENABLED=0` and uses `ZONAL_BUCKET_ARG` for zonal runs. Helper functions include `read_cache_test_setup`, `cleanup_test_environment`, `generate_config_file`, `run_read_cache_test`, and `run_chunk_cache_test` for the read-cache matrix. The rest of the script is a sequential set of `gcsfuse` or `mount.gcsfuse`, `go test`, and `sudo umount` blocks.

## Control Flow

The script validates the optional zonal argument, then runs package groups in a fixed order: operations, readonly, rename-dir-limit, implicit/explicit dirs, list/read/write large files, gzip/local-file/read-cache variants, managed folders, gRPC core tests, concurrent operations, benchmarking, kernel list cache, stale handle, streaming writes, inactive stream timeout, cloud profiler, readdirplus, dentry cache, buffered read, requester-pays, and flag optimizations. For read-cache, it generates config files and mounts for specific test cases and cache settings. Each scenario unmounts before moving to the next.

## State and Persistence Behavior

The script writes temporary config files under `/tmp`, log directories under `/tmp`, cache directories under `/tmp`, and repeatedly mutates the supplied mount directory state. It creates and deletes bucket content indirectly through tests. It does not install a global cleanup trap for every mount, so an early failure can leave the bucket mounted.

## Dependencies and Integration Points

It depends on `gcsfuse`, `mount.gcsfuse`, `go test`, `sudo umount`, Bash, and all integration packages it invokes. It is the mounted-directory counterpart to per-package harnesses and e2e CI scripts.

## Risks and Edge Cases

The script lacks `set -euo pipefail`, so failures may not stop subsequent scenarios unless individual commands exit the shell in the execution environment. Many variables are unquoted. It assumes sudo umount works and the mount directory is reusable after every scenario. Because it is long and sequential, one stale mount or leftover config/cache path can affect many later tests.

## Test Signals

Passing signal is successful completion of the entire sequential matrix without lingering mounts. Individual `go test` output identifies package-level failures. Readdirplus, read-cache, buffered-read, requester-pays, and flag-optimization sections provide targeted coverage for the files in this subset.
