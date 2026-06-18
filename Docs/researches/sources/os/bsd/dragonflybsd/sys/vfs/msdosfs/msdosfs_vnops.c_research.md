# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_vnops.c

## Role

Implements the DragonFly vnode operations for MSDOSFS files and directories. It adapts FAT directory-entry metadata and cluster chains to VFS create, access, getattr, setattr, read, write, fsync, remove, rename, mkdir, rmdir, readdir, bmap, and strategy operations.

## Major Entry Points

- `msdosfs_create()` creates regular files by generating a unique short name, setting FAT attributes, timestamps, and calling `createde()`.
- `msdosfs_access()`, `msdosfs_getattr()`, and `msdosfs_setattr()` translate FAT attributes, mount uid/gid/masks, timestamps, archive/read-only bits, and file size changes into VFS semantics.
- `msdosfs_read()` reads regular files through the file vnode and directories through the device vnode to avoid buffer-cache aliasing.
- `msdosfs_write()` extends FAT cluster chains, fills holes with zeroes via `deextend()`, updates buffer-cache blocks, and handles synchronous/unit writes.
- `msdosfs_fsync()` flushes vnode buffers, device metadata, and the denode’s directory entry.
- `msdosfs_remove()` and `msdosfs_rmdir()` remove directory entries and truncate deleted directory clusters.
- `msdosfs_rename()` implements file and directory renames, target replacement, denode rehashing, `..` repair, and directory-cycle prevention.
- `msdosfs_mkdir()` allocates a cluster, writes `.` and `..`, and inserts the parent directory entry.
- `msdosfs_readdir()` converts FAT directory entries and Win95 long-name entries into DragonFly `dirent` records.
- `msdosfs_bmap()` maps file offsets through FAT chains and reports contiguous run lengths.
- `msdosfs_strategy()` translates BIO offsets to backing device offsets and dispatches I/O to the mounted device vnode.
- `msdosfs_pathconf()` reports FAT name length, link count, chown restrictions, truncation, and file size bit limits.

## Implementation Notes

- DOS files are treated as always executable; owner write permission maps to clearing or setting `ATTR_READONLY`.
- Root-directory metadata is special: attribute changes are rejected because classic FAT root directories do not have self entries.
- File IDs in `getattr()` deliberately match `readdir()`’s `d_fileno` computation so tools such as `pwd` work.
- Reads of regular files support clustering and readahead; directory reads use `pm_devvp` because directory data and metadata share device-vnode cache identity.
- Writes pre-extend cluster chains to improve contiguity and roll back on `IO_UNIT` failure.
- Full-cluster writes can avoid read-before-write, except for `UIO_NOCOPY` where the buffer contents are not overwritten.
- Rename is complex because denode cache identity depends on directory cluster and offset; file renames across directories call `msdosfs_reinsert()`.
- Directory renames set `DE_RENAME` to block rmdir/rename races and use `doscheckpath()` when changing parents.
- `mkdir()` writes the child directory cluster before linking it from the parent, reducing crash exposure.
- `readdir()` synthesizes root `.`/`..`, skips deleted entries and volume labels, reconstructs long names with checksum validation, and supports NFS cookies.
- `bmap()` saves and restores the last FAT mapping cache after probing run lengths to avoid moving the sequential cache too far ahead.
- Symlinks, hard links, special nodes, and non-regular writes are unsupported.

## Dependencies

Uses denode metadata and cache operations, FAT allocation/truncation/mapping, lookup helper functions from `msdosfs_lookup.c`, buffer-cache clustering, vnode pager size updates, DragonFly old VOP interfaces, and FAT directory-entry conversion routines.

## Research Notes

This is the main behavioral surface for MSDOSFS. It consistently exposes a Unix-like vnode API while preserving FAT’s limitations: no hard links, no symlinks, no holes, fixed owner/group from mount options, and directory metadata stored directly in parent directory entries.
