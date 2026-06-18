<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs_test.go -->
# sources/user-network-fs/rclone/vfs/vfs_test.go

## Purpose
Provides the core VFS test harness and tests top-level VFS construction, interface defaults, stat/open/rename/statfs/directory operations, missing usage calculations, and metadata extension detection.

## Important APIs, Types, and Functions
Defines shared test times, writeback wait constants, `TestMain`, `cleanupVFS`, `newTestVFSOpt`, and `newTestVFS`. Tests include `TestVFSbaseHandle`, `TestVFSNew`, `TestVFSNewWithOpts`, `TestVFSRoot`, `TestVFSStat`, `TestVFSStatParent`, `TestVFSOpenFile`, `TestVFSRename`, `TestVFSStatfs`, `TestVFSMkdir`, `TestVFSMkdirAll`, `TestFillInMissingSizes`, and `TestVFSIsMetadataFile`.

## Control Flow
Helpers create `fstest` remotes and register cleanup that waits for writers, cleans cache, and shuts down VFS. Tests perform VFS API calls and compare returned nodes, errors, remote listings, usage values, and option-derived permissions.

## State and Persistence Behavior
Tests exercise active VFS cache refcounts, cache cleanup, root directory cache, remote object/directory mutations, usage cache, and metadata-extension option mutation. Directory tests skip when backend cannot have empty directories.

## Dependencies and Integration Points
Uses `fstest`, `vfscommon.Options`, `fs.Features`, and the package's `Dir`, `File`, and `Handle` implementations. Many other tests in this subset depend on its helpers and constants.

## Risks and Edge Cases
`TestVFSStatfs` has conditional expectations based on backend `About` support, so coverage varies. Directory tests skip on remotes without empty directories. Symlink APIs, `ReadDir`, `ReadFile`, `WriteFile`, `Chtimes`, `FlushDirCache`, and `WaitForWriters` failure logging are not fully tested here.

## Test Signals
Strong baseline signal for top-level VFS API compatibility with Go `os`-like behavior and for shared test setup used by the rest of the VFS tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs_test.go -->
