<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/mem_fs.go -->
# sources/storage-engines/pebble/vfs/mem_fs.go

## Purpose
Implements Pebble's in-memory `vfs.FS` and `vfs.File` for tests, including hard links, directory operations, file locks, optional Windows-like removal semantics, and crash-clone simulation for durability testing.

## Important APIs, Types, and Functions
`NewMem`, `NewCrashableMem`, and `NewMemFile` construct memory-backed filesystems/files. `MemFS` implements `FS` methods including `Create`, `Link`, `Open`, `OpenReadWrite`, `OpenDir`, `Remove`, `RemoveAll`, `Rename`, `ReuseForWrite`, `MkdirAll`, `Lock`, `List`, `Stat`, path helpers, disk usage stubbing, `CrashClone`, and `UnsafeGetFileDataBuffer`. `CrashCloneCfg`, `memNode`, `memFile`, `memFileInfo`, and `memFileLock` hold the backing tree, file handles, metadata, and lock state.

## Control Flow
All path operations route through `walk`, which strips leading slashes and traverses `memNode.children` under `MemFS.mu`. Mutations on crashable filesystems take `cloneMu.RLock`, while `CrashClone` takes `cloneMu.Lock` to block concurrent writes. Create replaces the final child with a new node. Link points a new directory entry at an existing node. Rename removes the old entry and inserts it at the new path. ReuseForWrite renames then opens the file write-only. File reads/writes lock the node's data mutex, update positions, grow buffers as needed, and optionally mutate input buffers when invariants are enabled.

## State and Persistence Behavior
Filesystem state is an in-memory tree. Directories store `children` and, when synced in crashable mode, `syncedChildren`. Files store `data`, `syncedData`, and `modTime`. `memFile.Sync` copies current file data or directory children into synced state; `CrashClone` returns a possible post-crash tree with all synced state plus optional random unsynced directory entries and 4 KiB data blocks. Open files increment node refs and close decrements them; Windows semantics reject removal of referenced nodes. `SyncTo` intentionally returns `(false, nil)` without durability to expose incorrect reliance on range sync.

## Dependencies and Integration Points
Implements the core `vfs.FS` contract used throughout Pebble tests. `Clone` and VFS datadriven tests use MemFS as a portable filesystem. WAL failover tests use `NewCrashableMem` to inspect durable log records after simulated crashes. `errNotEmpty` comes from platform error files.

## Risks and Edge Cases
`Rename` deletes the source before walking the destination; if destination parent traversal fails, the source has already been removed. This mirrors existing test utility assumptions but is not fully atomic. `Link` does not increment a link count; nodes persist as long as referenced by directory entries or open handles. `UnsafeGetFileDataBuffer` can race or corrupt state if misused. `f.readat` in the test harness appears to parse offset from the first argument rather than a second one, but that is test code, not MemFS itself.

## Test Signals
`mem_fs_test.go` covers datadriven basics, listing, crash-clone semantics, standalone mem files, crash clone concurrency against `ReuseForWrite`/`Link`/`Lock`, and lock behavior. `vfs_test.go` compares MemFS behavior with disk VFS for common operations and link/create semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/mem_fs.go -->
