<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fd_test.go -->
# sources/storage-engines/pebble/vfs/fd_test.go

## Purpose
Verifies VFS file wrappers preserve access to underlying OS file descriptors through `Fd`.

## Important APIs, Types, and Functions
`TestFileWrappersHaveFd` creates a real temporary file, wraps `vfs.Default` with disk health checks, opens a file, then wraps it with `NewSyncingFile` and asserts `Fd()` is nonzero and not `InvalidFd`.

## Control Flow
The test uses the default filesystem because `MemFS` returns `InvalidFd`. It checks the health-checking wrapper first, then the syncing wrapper stacked on top.

## State and Persistence Behavior
Creates and removes one temporary file. No durable Pebble data is involved.

## Dependencies and Integration Points
Covers wrapper compatibility with features that need descriptors, including fadvise and syncing-file range sync/preallocation. It relies on `WithDiskHealthChecks`, `Default.Open`, and `NewSyncingFile`.

## Risks and Edge Cases
Only checks descriptor availability, not descriptor correctness or behavior after close. It is sensitive to wrappers forgetting to forward `Fd`.

## Test Signals
Passing indicates descriptor-backed files remain usable through wrapper stacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fd_test.go -->
