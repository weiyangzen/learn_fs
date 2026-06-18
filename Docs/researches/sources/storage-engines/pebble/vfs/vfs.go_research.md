<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfs.go -->
# sources/storage-engines/pebble/vfs/vfs.go

## Purpose
Defines Pebble's filesystem abstraction and the default OS-backed implementation, plus portable helper functions for copying, link-or-copy fallback, read-hint open options, disk usage metadata, and wrapper unwrapping.

## Important APIs, Types, and Functions
`File`, `FS`, `OpenOption`, `DeviceID`, `FileInfo`, `DiskUsage`, `Default`, and `ErrUnsupported` form the public VFS contract. `defaultFS` implements filesystem operations through `os` and `filepath`. `RandomReadsOption` and `SequentialReadsOption` apply fadvise hints when possible. `Copy`, `CopyAcrossFS`, `LimitedCopy`, `LinkOrCopy`, and `Root` are utility functions.

## Control Flow
`defaultFS.Create` opens with `O_EXCL`; if a file exists, it removes and retries so hard-linked old inodes are not truncated. Open methods apply `OpenOption`s after wrapping OS files. Copy helpers open source and destination, stream bytes, and sync the destination. `LinkOrCopy` first tries a hard link, returns immediately for existence/not-existence/permission errors, and falls back to copy for other link failures. `Root` repeatedly calls `Unwrap` until it reaches the base FS.

## State and Persistence Behavior
The default FS delegates durability to OS file operations. Copy helpers call destination `Sync`; directory sync is left to callers. `Create` intentionally changes inode identity by removing existing files. `ReuseForWrite` renames an old file and opens it without truncation, enabling WAL recycling and similar reuse patterns.

## Dependencies and Integration Points
This interface underpins Pebble storage code, `MemFS`, `errorfs`, logging wrappers, syncing wrappers, WAL managers, and tests. Platform-specific files provide OS file wrapping, locking, errors, fadvise, sync range, and disk usage.

## Risks and Edge Cases
`Create` remove-then-create is not atomic, though it loops to handle races. `LinkOrCopy` chooses portability over precise cross-device detection, so unexpected link errors may trigger a copy attempt. `CopyAcrossFS` does not sync parent directories. `File.Write` explicitly allows mutation of input buffers, so callers must not assume buffer immutability.

## Test Signals
`vfs_test.go` exercises common operations on MemFS and disk FS, link/create semantics, disk usage, root opening, and operation string coverage. `fd_test.go`, lock tests, syncing tests, and MemFS tests cover related contract pieces.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfs.go -->
