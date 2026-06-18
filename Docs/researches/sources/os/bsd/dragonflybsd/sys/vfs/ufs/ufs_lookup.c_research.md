# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_lookup.c

## Purpose

Implements pathname component lookup within UFS directories and the directory-entry mutation helpers used by create, link, unlink, rename, mkdir, rmdir, whiteout, and symlink operations.

## Main Functions

- `ufs_lookup()`: central name lookup routine. Searches a directory for a component, optionally computes insertion/removal slot metadata, handles create/delete/rename semantics, lock-parent behavior, whiteouts, `.`/`..`, and vnode acquisition.
- `ufs_dirbad()` and `ufs_dirbadentry()`: report or validate malformed directory entries.
- `ufs_makedirentry()`: constructs a `struct direct` from an inode and `componentname`, including old-format byte-order handling.
- `ufs_direnter()`: inserts a new directory entry using slot information left by lookup. Handles new block allocation, compaction, dirhash updates, softdep ordering, async/sync writes, and directory truncation after compaction.
- `ufs_dirremove()`: removes or whiteouts a directory entry, updates dirhash, updates link counts, and schedules softdep remove work when enabled.
- `ufs_dirrewrite()`: rewrites an existing entry to point at a new inode, used by rename replacement.
- `ufs_dirempty()`: checks that a directory contains only `.` and `..`, ignoring empty and whiteout entries.
- `ufs_checkpath()`: prevents directory rename cycles by walking `..` from target toward root and checking whether source is encountered.

## Important Behavior

`ufs_lookup()` is both a lookup and planning routine. For create/rename/delete it records offsets in the directory inode:

- `i_offset`: target or insertion offset.
- `i_count`: previous-entry distance for deletion or available slot size for insertion.
- `i_reclen`: found entry record length.
- `i_endoff`: useful end of directory for possible truncation.

When `UFS_DIRHASH` is enabled, large directories can use dirhash for fast lookup and free-space discovery; otherwise the code performs a linear scan. Failed dirhash lookups can fall back to linear search.

Directory insertion may allocate a new directory block or compact an existing range. Soft updates receives explicit hooks so directory-entry writes are ordered after required inode/directory-body writes.

## Dependencies And Integration Points

Uses `ffs_blkatoff()`, `VOP_BALLOC()`, `ffs_update()`, `ffs_truncate()`, vnode locking, `VFS_VGET()`, dirhash helpers, and softdep hooks from `ufs_extern.h`.

## Notes For Future Work

- Old UFS directory format is handled with the `OFSFMT()` macro and little-endian field swapping.
- `dirchk` controls expensive directory-entry validation through a debug sysctl.
- Several code paths intentionally unlock a parent before fetching `..` to avoid directory-tree deadlocks.
- The directory mutation helpers depend on `ufs_lookup()` leaving valid slot metadata while the parent directory remains locked.
