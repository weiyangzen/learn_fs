# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_vnops.c

## Purpose
Implements the common UFS vnode operation vectors and most user-visible filesystem behavior: create, remove, link, rename, mkdir/rmdir, symlink, attributes, access checks, readdir, readlink, strategy I/O, pathconf, vnode initialization, and FIFO wrapping.

## Key vnode operations
- Creation: `ufs_create()`, `ufs_mknod()`, `ufs_makeinode()`, `ufs_mkdir()`, `ufs_symlink()`.
- Removal and link changes: `ufs_remove()`, `ufs_link()`, `ufs_rmdir()`, `ufs_rename()`, `ufs_whiteout()`.
- Access and metadata: `ufs_accessx()`, `ufs_fplookup_vexec()`, `ufs_stat()`, `ufs_getattr()`, `ufs_setattr()`, `ufs_chmod()`, `ufs_chown()`, `ufs_itimes()`.
- Directory and symlink reads: `ufs_readdir()`, `ufs_readlink()`.
- I/O mapping and dispatch: `ufs_strategy()`, `ufs_ioctl()`, `ufs_read_pgcache()`.
- Vnode setup and diagnostics: `ufs_vinit()`, `ufs_print()`, `ufs_pathconf()`.
- Registered vectors: `ufs_vnodeops` and `ufs_fifoops`.

## Timestamp and metadata handling
`ufs_itimes_locked()` applies pending access/change/update flags to inode timestamps unless the filesystem is read-only. It marks inodes modified, lazy-modified, or lazy-accessed depending on vnode type, softdep state, and mount suspension. `ufs_stat()` and `ufs_getattr()` flush pending times under the vnode interlock before reporting attributes.

`ufs_setattr()` validates unsupported fields, enforces read-only and snapshot restrictions, handles file flags with securelevel and jail-aware privilege rules, truncates regular files/symlinks, updates timestamps and birthtime, and delegates mode and ownership changes.

## Access control
`ufs_accessx()` blocks writes to read-only mounts for normal file objects, initializes quotas on exclusive write opens, rejects modification of immutable or snapshot inodes, and then evaluates ACLs when enabled or falls back to Unix permission checks. `ufs_fplookup_vexec()` provides a lockless SMR fast path for execute permission during path lookup, returning `EAGAIN` if inode state cannot be safely read.

## Link and rename behavior
`ufs_link()` guards link-count limits with `ufs_sync_nlink()`, rejects unlinked/immutable/append-only sources, increments effective and on-disk link counts, sets up softdep link state, and inserts a directory entry.

`ufs_rename()` is the largest operation. It:
- Drops initial locks and reacquires `fdvp`, `tdvp`, `fvp`, and optional `tvp` in a restartable order.
- Revalidates source and target names with `ufs_lookup_ino()`.
- Supports `AT_RENAME_NOREPLACE` and rejects unsupported flags.
- Uses sequence counters around vnode namespace modification.
- Handles soft updates journaling preflight with `softdep_prerename()`.
- Prevents cross-device renames, mounted-on directory renames, rename cycles, sticky-directory violations, and incompatible file/directory replacement.
- Temporarily bumps the source link count to keep it alive.
- Creates or rewrites the target entry, removes the source entry, updates `..` when moving directories, and purges/updates namecache state.

`rename_restarts` records restarts caused by lock contention or revalidation races.

## Directory creation and removal
`ufs_mkdir()` manually allocates and initializes a directory inode, writes `.` and `..` from the static templates, updates parent link counts before exposing the new entry, applies MAC labels and ACL inheritance, then inserts the name in the parent directory.

`ufs_rmdir()` verifies the parent link count, checks emptiness, rejects append/immutable/nounlink and mounted-on directories, handles softdep journaling preflight, removes the parent entry, updates link counts, purges cache state, and frees any active dirhash.

## ACL, MAC, quota, and optional feature integration
The file conditionally supports:
- UFS quotas, including quota setup and accounting during create/chown/mkdir.
- POSIX.1e and NFSv4 ACL inheritance and mode synchronization.
- MAC multilabel extended attributes on create and mkdir.
- GEOM journaling orphan tracking on remove/rmdir.
- `SUIDDIR` ownership inheritance.
- Directory hash cleanup.
- Fast page-cache reads for suitable regular files.

## Directory and symlink reads
`ufs_readdir()` walks raw UFS directory entries, validates record lengths, translates old-format fields if needed, emits generic `struct dirent` records, fills NFS cookies when requested, and reports EOF based on inode size.

`ufs_readlink()` serves short symlinks directly from inode storage when smaller than `um_maxsymlinklen`; longer symlinks are read through `VOP_READ`.

## I/O and vnode vectors
`ufs_strategy()` maps logical to physical blocks through `ufs_bmaparray()` before submitting buffers to the mount buffer object. Holes are zero-filled and completed without device I/O.

`ufs_vnodeops` registers common UFS vnode operations while leaving filesystem-specific read/write/fsync/reallocblks as panics here, because FFS supplies those implementations. `ufs_fifoops` wraps FIFO special operations while preserving UFS metadata, inactive, reclaim, access, and attribute behavior.

## Research notes
This file is the main user-facing UFS operation layer. It delegates block allocation, truncation, update, inode allocation/free, and read/write implementation through `ufsmount` callbacks or FFS-specific vectors, while centralizing namespace semantics, permission checks, metadata policy, and vnode operation registration.
