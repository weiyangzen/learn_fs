<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file_linux_test.go -->
# sources/storage-engines/pebble/vfs/syncing_file_linux_test.go

## Purpose
Provides Linux-specific tests and benchmarks for range syncing and direct IO write behavior.

## Important APIs, Types, and Functions
`TestSyncRangeSmokeTest` exercises `syncRangeSmokeTest` with injected syscall outcomes. `BenchmarkDirectIOWrite` measures aligned `O_DIRECT` writes across write sizes.

## Control Flow
The smoke test passes a fake sync-range function that validates the fd and returns nil, `EINVAL`, or `ENOSYS`; expected support is true for nil and `EINVAL`, false for `ENOSYS`. The benchmark creates a temp file, aligns a buffer to 4096 bytes, opens with `O_DIRECT`, writes at offsets until a target size, and cycles files.

## State and Persistence Behavior
The test itself does not persist Pebble data. The benchmark writes temporary files and syncs them to measure IO behavior.

## Dependencies and Integration Points
Covers Linux-only `SyncTo` support used by `syncing_file.go`. Depends on `syscall`, `unsafe`, and Linux `O_DIRECT`; build tag excludes ARM.

## Risks and Edge Cases
Benchmarks require filesystem support for `O_DIRECT` and alignment-sensitive behavior. The smoke test treats `EINVAL` as support because some kernels/filesystems may reject specific arguments while still supporting the syscall.

## Test Signals
Passing confirms the sync-range feature probe classifies common syscall responses as expected.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file_linux_test.go -->
