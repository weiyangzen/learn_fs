<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_windows.go -->
# sources/storage-engines/pebble/vfs/errors_windows.go

## Purpose
Defines Windows-specific filesystem error helpers for Pebble's VFS layer.

## Important APIs, Types, and Functions
`errNotEmpty` aliases `windows.ERROR_DIR_NOT_EMPTY`. `IsNoSpaceError` recognizes `windows.ERROR_DISK_FULL` and `windows.ERROR_HANDLE_DISK_FULL` through CockroachDB error wrapping.

## Control Flow
`IsNoSpaceError` performs two `errors.Is` checks and returns true if either Windows error code is in the error chain.

## State and Persistence Behavior
No state or persistence. It only supplies platform-specific constants and classification.

## Dependencies and Integration Points
Used by VFS callers that need portable disk-full detection and by MemFS removal behavior through `errNotEmpty`. Built only on Windows.

## Risks and Edge Cases
The helper intentionally recognizes disk-full conditions, not every storage-related Windows error. There is no local Windows-specific test in this shard.

## Test Signals
No direct test file is listed for Windows. Unix coverage in `errors_unix_test.go` provides analogous expectations for wrapped-error matching.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_windows.go -->
