<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/open_files_test.go -->
# sources/storage-engines/pebble/vfs/vfstest/open_files_test.go

## Purpose
Tests the open-file tracking VFS wrapper.

## Important APIs, Types, and Functions
`TestOpenFiles` uses `WithOpenFileTracking`, a MemFS, and a table of file-opening operations: `OpenDir`, `Create`, `Open`, `OpenReadWrite`, and `ReuseForWrite`.

## Control Flow
The test prepares a directory and file operations, then runs two subtests. In `leaks`, each operation opens a file, dumps stacks, asserts output exists, closes the file, and asserts the dump is empty. In `noleaks`, it opens and closes before dumping and expects no output.

## State and Persistence Behavior
State is an in-memory MemFS plus tracking map. `ReuseForWrite` renames `foo` to `bar`, so the operation sequence relies on the surrounding setup and subtest order.

## Dependencies and Integration Points
Covers `open_files.go` and the VFS file-opening methods. It validates the wrapper as a reusable test diagnostic.

## Risks and Edge Cases
The test only asserts non-empty dump output, not exact stack contents. It does not cover open failures or lock handles.

## Test Signals
Passing confirms tracked files are registered on open/create/reuse and unregistered on close.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/open_files_test.go -->
