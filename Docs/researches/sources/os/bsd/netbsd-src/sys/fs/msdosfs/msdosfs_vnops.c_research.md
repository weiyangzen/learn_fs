# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_vnops.c

## Summary
Implements vnode operations for msdosfs regular files and directories. It handles create, close, access, getattr/setattr, read/write, metadata update, remove, mkdir/rmdir, readdir, bmap, strategy, advisory locks, pathconf, fsync, timestamp conversion, and the vnode operation dispatch table.

## Main Responsibilities
- Create regular files with `msdosfs_create()`, generating unique DOS aliases, initializing denode metadata, creating directory entries, and populating the name cache.
- Update access timestamps on close while files remain referenced.
- Enforce access with read-only filesystem checks and DOS readonly-bit-to-mode translation in `msdosfs_access()`.
- Fill Unix-style attributes in `msdosfs_getattr()`, including file IDs aligned with `readdir`, mount uid/gid, mode masks, FAT timestamps, archive bit projection, size, and block usage.
- Apply supported attributes in `msdosfs_setattr()`: size truncation/extension, atime/mtime, readonly bit from owner-write mode, and archive flag.
- Read regular files through UBC and directories through device-vnode buffer I/O in `msdosfs_read()`.
- Write regular files through UBC in `msdosfs_write()`, pre-extending FAT chains for contiguous allocation, zero-filling holes because FAT has no sparse files, enforcing the 32-bit FAT file size limit, flushing on sync writes, and truncating back on write failure.
- Persist denode metadata into directory entries with `msdosfs_update()`.
- Remove non-directories with `msdosfs_remove()`.
- Create directories with `msdosfs_mkdir()`, allocating one cluster, initializing `.` and `..`, writing it before linking from the parent, then creating the parent directory entry.
- Remove empty directories with `msdosfs_rmdir()`, rejecting `.` and `DE_RENAME` directories, deleting the parent entry, purging cache, and truncating the removed directory.
- Convert FAT directory entries to `struct dirent` records in `msdosfs_readdir()`, including synthetic root `.`/`..`, Win95 long-name assembly, short-name fallback, cookies, file IDs, and EOF reporting.
- Map file clusters to device blocks with `msdosfs_bmap()` and contiguous run discovery.
- Submit buffer I/O to the underlying device vnode in `msdosfs_strategy()`.
- Provide diagnostics, advisory locks, pathconf limits, fsync/cache sync, and timestamp conversion helpers.
- Define `msdosfs_vnodeop_entries` and `msdosfs_vnodeop_opv_desc`.

## Key Interfaces
- VOP handlers: `msdosfs_create`, `msdosfs_close`, `msdosfs_access`, `msdosfs_getattr`, `msdosfs_setattr`, `msdosfs_read`, `msdosfs_write`, `msdosfs_remove`, `msdosfs_mkdir`, `msdosfs_rmdir`, `msdosfs_readdir`, `msdosfs_bmap`, `msdosfs_strategy`, `msdosfs_print`, `msdosfs_advlock`, `msdosfs_pathconf`, and `msdosfs_fsync`.
- Metadata helpers: `msdosfs_update()` and `msdosfs_detimes()`.
- Operation vector exports: `msdosfs_vnodeop_p`, `msdosfs_vnodeop_entries`, and `msdosfs_vnodeop_opv_desc`.

## Risks
Regular-file I/O uses UBC while directory I/O uses the filesystem device vnode to avoid buffer-cache aliasing with directory metadata. Writes pre-extend files and must roll back on failure; any failure after FAT allocation can interact with truncation and metadata update paths. Directory creation writes the new directory cluster before linking it for crash-ordering reasons but the filesystem is still non-journaled. `msdosfs_update()` skips writing directory denodes and removed entries, relying on directory-entry update paths elsewhere. `readdir` long-name reconstruction depends on checksum continuity and falls back to short names when long-name entries are missing or corrupt.
