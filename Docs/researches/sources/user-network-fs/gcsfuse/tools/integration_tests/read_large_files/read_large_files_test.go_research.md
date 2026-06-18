# sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/read_large_files_test.go

## Purpose

This is the package harness for large-file read tests. It defines size constants and configures GCSFuse runs that exercise normal reads, gRPC, file cache with range caching, unlimited file cache, and a zonal-bucket-specific kernel-reader-disabled path.

## Important APIs, Types, and Functions

Constants define `FiveHundredMB`, sequential `ChunkSize`, random chunk size, number of random reads, offset bounds, and `DirForReadLargeFilesTests`. Package globals store `storageClient`, `ctx`, and a random file name. `TestMain` controls config loading, storage client lifecycle, mounted-directory mode, path rewriting, flag-set generation, and static mount execution.

## Control Flow

`TestMain` parses flags, synthesizes `ReadLargeFiles` config if needed, sets up environment and storage client, optionally delegates to mounted-directory mode, prepares the bucket test directory, rewrites `/gcsfuse-tmp` cache paths, builds compatible flag sets, and runs the tests via `static_mounting.RunTestsWithConfigFile`.

## State and Persistence Behavior

The harness creates bucket prefixes and local cache directories under the test temp root. It maintains a storage client for the package lifetime and relies on helper cleanup for generated large files and bucket directories. It does not run dynamic or persistent mounts.

## Dependencies and Integration Points

It depends on Google Cloud Storage client setup, `operations.MiB`, setup/test-suite helpers, and static mounting. Sibling tests consume the size and directory constants.

## Risks and Edge Cases

The default flag matrix includes expensive 500 MiB workloads with a 700 MiB file-cache limit, so tests can stress disk and runtime. Zonal bucket compatibility differs from flat/HNS for one config item. Cache path rewriting must occur before flag-set expansion. Mounted-directory mode requires both bucket and mount so local-vs-mounted validation remains meaningful.

## Test Signals

Package-level success across the flag matrix proves large sequential, random, and concurrent reads return correct content under multiple read/cache configurations. Setup failures usually indicate bucket, build, mount, or local resource problems.
