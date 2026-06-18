# File Research: sources/os/linux/linux-stable/fs/coda/dir.c

## Purpose
Implements Coda directory inode operations, permission checks, dentry revalidation/deletion, directory reading, and inode revalidation.

## Main Interfaces
- VFS directory operations: `coda_lookup()`, `coda_create()`, `coda_mkdir()`, `coda_link()`, `coda_symlink()`, `coda_unlink()`, `coda_rmdir()`, `coda_rename()`.
- Permission/revalidation: `coda_permission()`, `coda_revalidate_inode()`.
- Directory reading: `coda_readdir()`, internal `coda_venus_readdir()`.
- Operation tables: `coda_dentry_operations`, `coda_dir_inode_operations`, `coda_dir_operations`.

## Control Flow
Lookup rejects overlong names, synthesizes the root `.CONTROL` inode locally, or calls `venus_lookup()` and creates a cnode from the returned FID. Entries marked `CODA_NOCACHE` are flagged with `C_VATTR | C_PURGE`.

Permission checks do not support RCU mode, validate execute permission locally, consult the Coda permission cache, and call `venus_access()` on cache miss. Successful access is cached per fsuid/mask.

Create, mkdir, link, symlink, unlink, rmdir, and rename are thin VFS wrappers around Venus upcalls. They update parent mtimes, instantiate or drop dentries, and adjust link counts optimistically where possible. Control object creation at the root is forbidden.

Directory iteration first tries `iterate_dir()` on the Venus-provided container file. If that returns `-ENOTDIR`, it reads Venus-format `venus_dirent` records manually, validates record lengths, skips `.`/`..`, maps Coda d_types to Linux `DT_*`, and emits entries.

Dentry revalidation interprets `C_PURGE` and `C_FLUSH` flags, shrinks child dentries, propagates flush to children, and unhashed stale dentries when their count allows it. Inode revalidation refetches attributes from Venus when flags require it and clears stale flags.

## State And Synchronization
Coda inode flags are protected by `c_lock`. Dentry validity is coordinated through Coda flags plus VFS dentry counts. Directory mtime/link count updates are optimistic unless configured to requery Venus.

## Integration Points
Depends heavily on Venus upcalls declared in `coda_psdev.h`, cnode creation from `cnode.c`, permission cache from `cache.c`, and attribute conversion from `coda_linux.c`.

## Risks And Review Focus
- Venus directory file parsing must reject short or malformed records.
- Rename/link count updates are optimistic and must tolerate Venus-specific volume mount behavior.
- Dentry revalidation returns valid for busy stale dentries, leaving flags for later cleanup.
