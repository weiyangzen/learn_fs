# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_dir.c

## Purpose

`ufs_dir.c` implements UFS directory namespace manipulation: lookup, create, link, symlink insertion, rename, removal, directory emptiness checks, path-cycle prevention, and extended-attribute directory creation. It is the core directory-entry layer under the higher UFS vnode operations.

The file treats directory mutation as serialized by `i_rwlock`; its header notes that directories cannot be mmaped, so `i_contents` is redundant for some namespace serialization but is still used where inode fields and page/block operations require it.

## Main Interfaces

Public entry points include:

- `ufs_diraccess()` checks that an inode is a directory or attribute directory and delegates permission checks to `ufs_iaccess()`.
- `ufs_dirlook()` resolves a name to a held inode, using DNLC individual-name caching and optional whole-directory DNLC caching.
- `ufs_direnter_cm()` creates regular entries for create/mkdir/attribute-dir style operations, allocating a new inode when needed.
- `ufs_direnter_lr()` handles link, symlink, and rename insertion paths that already have a source inode.
- `ufs_dircheckforname()` scans a directory for an existing name and/or a free slot for a new entry.
- `ufs_dirmakeinode()` allocates and initializes an inode before it is linked into a directory.
- `ufs_dirremove()` removes names for unlink, rmdir, and rename cleanup.
- `blkatoff()` returns a mapped fbuf containing a directory block at a given offset.
- `ufs_dircheckpath()` walks `..` links to prevent moving a directory under itself.
- `ufs_xattrdirempty()` and `ufs_xattrmkdir()` implement extended-attribute directory support.

Important private helpers include `ufs_dirrename()`, `ufs_dirfixdotdot()`, `ufs_diraddentry()`, `dirprepareentry()`, `ufs_dirmakedirect()`, `ufs_dirempty()`, `ufs_dirpurgedotdot()`, `ufs_dirscan()`, `ufs_dirclrdotdot()`, `dirmangled()`, `dirbad()`, and `dirbadname()`.

## Directory Lookup And Caching

`ufs_dirlook()` first checks the ordinary DNLC. Negative entries use `DNLC_NO_VNODE` when `ufs_negative_cache` is enabled and the directory still has links. It then uses the directory-wide DNLC cache rooted at `i_danchor`; UFS packs a 32-bit inode number and a 32-bit directory offset into the DNLC directory handle with `INO_OFF_TO_H()`.

For large directories, controlled by `ufs_min_dir_cache`, the code attempts whole-directory caching through `dnlc_dir_start()`. Memory pressure disables caching briefly with `CD_DISABLED_NOMEM` and `ufs_dc_disable_duration`; directories that are too large are marked `CD_DISABLED_TOOBIG`.

Lookup has special handling for `"."` and `".."`. `"."` can hold the directory vnode directly. `".."` may require dropping the directory `i_rwlock` before `ufs_iget_alloced()` to avoid deadlock, then revalidating the entry with timestamps or a second directory cache lookup because the parent could have changed while the lock was dropped.

When scanning directory blocks, the code advances by `d_reclen`, validates alignment and record length, and optionally runs full checks with the `dirchk` tunable. Bad records are skipped to the next `DIRBLKSIZ` block; if whole-directory caching was active, the cache is purged because the scan no longer has reliable complete information.

## Entry Creation And Slot Management

`ufs_direnter_cm()` handles create/mkdir/attribute-dir operations. It rejects invalid entries in attribute directories, forbids slash in component names, handles `"."` and `".."` as existing entries, checks execute/write access, calls `ufs_dircheckforname()`, and creates a new inode with `ufs_dirmakeinode()` before installing the entry with `ufs_diraddentry()`.

`ufs_dircheckforname()` serves two roles: find an existing name and find usable free space. It can use the directory DNLC cache both for existing entries and free-space handles. Without cache coverage it scans the whole directory, tracks the last useful offset for possible truncation, and returns a `ufs_slot` describing either an existing entry, a reusable record, or a new block at the rounded-up end of the directory.

`dirprepareentry()` turns a returned slot into writable directory-entry space. If no slot exists, it allocates a new `DIRBLKSIZ` block with `BMAPALLOC()` and extends `i_size`. If a slot exists inside an occupied record, it splits the record by shrinking the old entry to `DIRSIZ(ep)` and placing the new entry in the remainder.

`ufs_diraddentry()` fills `d_namlen`, `d_name`, and `d_ino`, updates normal DNLC and directory DNLC state, records the directory block with `TRANS_DIR()`, writes it with `ufs_fbwrite()`, marks the parent inode changed, and may truncate trailing empty directory space when not logging.

## Inode Creation

`ufs_dirmakeinode()` allocates a UFS inode near the parent or preferred directory cylinder group, sets type/mode, UID/GID, legacy 16-bit `i_suid`/`i_sgid` compatibility fields, device numbers, set-GID inheritance, quota attachment, ACL inheritance, xattr flags, and timestamps. It writes the inode synchronously before a name points to it.

For new directories and attribute directories, `ufs_dirmakedirect()` allocates the first directory block, writes the `.` and `..` template, updates the parent link count for normal directories, logs the directory block, and writes it.

Extended attribute directories are built with `ufs_xattrmkdir()`, which uses lockfs protocol, synchronous mkdir transactions, special IFATTRDIR modes, optional attachment to the owning inode via `i_oeftflag`, xattr vnode flags, and a retry path that drains delayed deletes if inode exhaustion occurs under logging.

## Rename And Removal

`ufs_direnter_lr()` prepares link, symlink, and rename operations by syncing source inode data and indirect blocks before incrementing link counts and exposing directory entries. If insertion later fails, it rolls back the source link count for non-symlink operations.

`ufs_dirrename()` replaces an existing target entry with the source inode. It avoids deadlocks by try-locking peer inode contents locks, checks same-filesystem constraints, sticky-directory permissions, type compatibility, mountpoint busy state, target-directory emptiness, and then rewrites the target `d_ino` before decrementing the overwritten inode. Directory rename across parents calls `ufs_dirfixdotdot()` to update the child `..` entry and adjust parent link counts.

`ufs_dirremove()` handles unlink/rmdir removal. It rejects empty names and removal of `"."` or `".."`, checks directory write/search access, obtains the target inode, handles mounted directories through `vn_vfsrlock()`, try-locks child directory `i_rwlock` to avoid rename cycles, applies sticky-directory checks, validates rmdir conditions, removes DNLC entries, clears `d_ino`, coalesces directory free space, logs/writes the directory block, decrements link counts, and purges `.`/`..` for removed directories.

`ufs_dircheckpath()` walks upward through `..` entries from a target directory to ensure a source directory is not in the target path. It uses try-lock/backoff behavior to avoid rename deadlocks and returns `EAGAIN` if a writer-wanted state could produce a cycle.

## Invariants And Dependencies

Key invariants:

- Callers generally hold target directory `i_rwlock` as writer for mutation.
- Directory block updates must be recorded through `TRANS_DIR()` before `ufs_fbwrite()`.
- New inodes are written before directory entries point to them.
- Directory rename must keep target entry replacement, target link-count decrements, and `..` repair ordered carefully.
- Whole-directory DNLC cache entries carry previous-entry offsets; cache updates must track record splitting/coalescing.
- Attribute directories use IFATTRDIR semantics and have different quota/link-count behavior.

This file depends on inode allocation and truncation (`ufs_ialloc`, `ufs_itrunc`, `ufs_iupdat`), block mapping (`BMAPALLOC`, `blkatoff`, `ufs_rdwri`), transaction logging (`TRANS_DIR`, `TRANS_INODE`), DNLC directory-cache APIs, quota locks (`vfs_dqrwlock`), xattr/ACL inheritance, vnode mount locking, and lockfs support.

## Research Notes

Audit hotspots are rename rollback after `..` repair, DNLC directory-cache offset correctness during split/coalesce, rmdir behavior with hard-linked directories or attribute directories, lock dropping around `".."` lookup, and any path that returns `EAGAIN` for deadlock avoidance. Directory corruption handling intentionally skips bad records rather than repairing them in place.
