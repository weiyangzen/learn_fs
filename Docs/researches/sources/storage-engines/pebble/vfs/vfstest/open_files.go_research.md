<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/open_files.go -->
# sources/storage-engines/pebble/vfs/vfstest/open_files.go

## Purpose
Provides a test wrapper that tracks currently open files and can dump the stack traces that opened them. It helps diagnose leaked VFS file handles in tests.

## Important APIs, Types, and Functions
`WithOpenFileTracking` wraps an inner `vfs.FS` and returns the wrapped FS plus a dump function. `openFilesFS` implements `vfs.FS`. `openFile` wraps `vfs.File`, stores caller PCs, dumps stack frames, and removes itself from tracking on `Close`.

## Control Flow
All FS methods that open or create files call `wrapOpenFile`. If the open succeeds, `runtime.Callers` captures the call stack, the file is inserted into the `files` map under mutex, and the wrapper is returned. `dumpStacks` prints a count and each open file's captured stack. Closing an `openFile` delegates close then removes it from the map.

## State and Persistence Behavior
State is in-memory tracking metadata only: a mutex-protected map of open wrapper pointers and captured PCs. Underlying filesystem state is delegated unchanged.

## Dependencies and Integration Points
Part of package `vfstest`, used by tests that need leak diagnostics around any `vfs.FS`. It implements `Unwrap` so root unwrapping still works.

## Risks and Edge Cases
If the underlying `Close` returns an error, the file is still removed from tracking. Lock handles are not tracked because `Lock` returns `io.Closer`, not `vfs.File`. Stack depth is capped at 20 PCs.

## Test Signals
`open_files_test.go` verifies every file-opening method reports a leak before close and reports nothing after close.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/open_files.go -->
