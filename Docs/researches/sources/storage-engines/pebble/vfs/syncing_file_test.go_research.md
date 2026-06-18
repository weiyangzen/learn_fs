<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file_test.go -->
# sources/storage-engines/pebble/vfs/syncing_file_test.go

## Purpose
Tests `syncingFile` range-sync thresholds, close-time durability behavior, `NoSyncOnClose`, and provides sync write benchmarks.

## Important APIs, Types, and Functions
`TestSyncingFile`, `TestSyncingFileClose`, `mockSyncToFile`, `TestSyncingFileNoSyncOnClose`, and `BenchmarkSyncWrite` are the main elements. `mockSyncToFile` lets tests force partial `SyncTo` behavior or full-sync fallback behavior.

## Control Flow
`TestSyncingFile` writes increasing amounts and checks expected `syncOffset` values after the 1 MiB buffer and 8 KiB threshold. `TestSyncingFileClose` logs sync/close calls through `vfsTestFSFile` and compares expected output for partial versus full-syncing files. `TestSyncingFileNoSyncOnClose` verifies close ratchets sync offset without blocking full sync when configured. The benchmark compares no preallocation, 4 MiB preallocation, and reuse scenarios.

## State and Persistence Behavior
Tests create temporary OS files and remove them afterward. They inspect in-memory offsets and logged sync calls rather than reopening files for durable content. Benchmarks perform real syncs and optional preallocation/reuse on temp files.

## Dependencies and Integration Points
Covers `syncing_file.go`, the default VFS file wrapper, and the VFS logging test wrapper. It also documents expectations for callers such as WAL writing.

## Risks and Edge Cases
The tests assert internal `syncingFile` state, so implementation refactors must preserve thresholds or adjust tests. Benchmarks are performance-only and not correctness gates.

## Test Signals
Passing confirms periodic range-sync decisions, close-time full sync when needed, and `NoSyncOnClose` behavior match the intended contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file_test.go -->
