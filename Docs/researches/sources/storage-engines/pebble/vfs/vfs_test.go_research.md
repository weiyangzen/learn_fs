<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfs_test.go -->
# sources/storage-engines/pebble/vfs/vfs_test.go

## Purpose
Provides datadriven and targeted tests for the VFS abstraction across MemFS and the default disk filesystem.

## Important APIs, Types, and Functions
`normalizeError`, `vfsTestFS`, `vfsTestFSFile`, `runTestVFS`, `TestVFS`, `TestVFSGetDiskUsage`, `TestVFSCreateLinkSemantics`, `TestVFSRootDirName`, and `TestOpType` are the main components.

## Control Flow
`runTestVFS` wraps an FS with logging and interprets fixture commands for clone, create, link, link-or-copy, reuse-for-write, list, mkdir, remove, and remove-all. It can inject a link error to test fallback behavior. Targeted tests check disk usage on a real temp dir, hard-link behavior when `Create` replaces a linked path, opening root directories, and string coverage for operation types.

## State and Persistence Behavior
Tests create temporary directories/files for disk VFS and use MemFS for in-memory runs. They verify `Create` on one hard link does not truncate the other link and that clone operations produce expected logs and content.

## Dependencies and Integration Points
Covers `vfs.go`, `MemFS`, clone helpers, path helpers, and error normalization through `oserror`. It serves as a cross-implementation contract test.

## Risks and Edge Cases
Disk tests are skipped on Windows for the main datadriven VFS run, so some disk behavior is only covered on non-Windows platforms. Logging wrappers in the test are specialized and not the same as `logging_fs.go`.

## Test Signals
Passing confirms MemFS and default FS share core semantics, `LinkOrCopy` behaves under injected link errors, disk usage can be queried, root directories open, and operation string coverage stays complete.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfs_test.go -->
