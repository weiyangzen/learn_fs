<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_dir_with_twelve_thousand_files_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_dir_with_twelve_thousand_files_test.go

## Purpose

This file stress-tests listing a directory containing 12,000 files and optional explicit and implicit subdirectories. It also checks that kernel list cache improves repeated listing latency when enabled.

## Important APIs, Types, and Functions

`listLargeDir` is a Testify suite with `flags` and `isKernelListCacheEnabled`. Helpers include `validateDirectory`, `checkIfObjNameIsCorrect`, `testdataUploadFilesToBucket`, `createFilesAndUpload`, `listDirTime`, `testdataCreateImplicitDir`, `testdataCreateExplicitDir`, and `prepareTestDirectory`. Tests cover files only, files plus explicit dirs, and files plus explicit and implicit dirs.

## Control Flow

Setup deletes any existing objects under the test name and mounts with current flags. `prepareTestDirectory` creates the mounted directory, generates 12,000 local files under `$HOME`, uploads them in batch, and optionally creates 100 explicit managed directory markers and 100 implicit directories via nested object copies. `listDirTime` records the first `os.ReadDir`, validates entry names/counts, then performs five more reads and returns the fastest repeated listing. Tests assert repeated reads are less than half the first read when kernel list cache is enabled.

## State and Persistence Behavior

Large temporary local file trees are created and removed under `$HOME`. Backing GCS state contains thousands of objects and directory markers. Kernel list cache state is inferred from repeated listing time, not direct counters.

## Dependencies and Integration Points

It uses Cloud Storage batch upload/copy/create-dir helpers, `errgroup` for explicit dir creation, goroutines with a semaphore for implicit dirs, and the package setup's static mount config. It skips implicit-dir coverage for zonal buckets.

## Risks and Test Signals

This is resource and timing heavy. Performance assertions can be noisy on busy systems, and validation assumes prefixes encode numeric ranges. Passing signals are exact entry counts/names and a clear cached-listing speedup when the kernel list cache variant runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_dir_with_twelve_thousand_files_test.go -->
