<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/multizip.go -->
# sources/user-network-fs/go-fuse/zipfs/multizip.go

## Purpose
Implements a dynamic archive-mounting filesystem where symlinks under `/config` mount archive trees at root-level names.

## Important APIs, Types, and Functions
`MultiZipFs.OnAdd`, `configRoot.Unlink`, and `configRoot.Symlink` define behavior.

## Control Flow
On add, the root creates `/config`. Creating a symlink in `/config/<name>` opens the target archive with `NewArchiveFileSystem`, adds it as `/<name>`, and stores a memory symlink under config. Unlink removes both views.

## State and Persistence Behavior
Persistent state is in the in-memory inode tree, not on disk. Mounted archive contents are immutable child inode trees.

## Dependencies and Integration Points
Depends on go-fuse persistent inodes, `NewArchiveFileSystem`, and `fs.MemSymlink`.

## Risks and Edge Cases
`Unlink` calls `RmChild` twice and may race with cache invalidation. Archive paths are trusted and opened from the host. Root remains read-only except dynamic mounts.

## Test Signals
`multizip_test.go` covers readonly behavior, dynamic mount, readlink, archive access, and removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/multizip.go -->
