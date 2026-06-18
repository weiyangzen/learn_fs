# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vfsops.c

Purpose: Provides NetBSD VFS operations for CHFS mount lifecycle, vnode loading, statvfs, module registration, and global initialization.

Key entry points:
- `chfs_mount`: validates mount args/device, opens block device, calls `chfs_mountfs`.
- `chfs_mountfs`: initializes CHFS mount state and EBH, scans/builds filesystem, creates root vnode, starts GC.
- `chfs_unmount`: stops GC, flushes write buffer, frees refs/cache, closes EBH/device, destroys locks.
- `chfs_root`, `chfs_vget`, `chfs_loadvnode`: vnode creation/loading.
- `chfs_statvfs`: reports eraseblock-based space stats.
- `chfs_init`, `chfs_reinit`, `chfs_done`: module/global pool lifecycle.
- `chfs_modcmd`: attach/detach VFS module.

Important behavior:
- CHFS is mounted only over a block device whose major matches the flash cdevsw major.
- `struct ufsmount` is reused as integration scaffolding, with `um_chfs` pointing to CHFS mount state.
- Mount initializes queues, locks, write buffer, EBH, block array, free/dirty accounting, and trigger levels before `chfs_build_filesystem`.
- Root inode is synthetic/in-memory and uses `CHFS_ROOTINO`.
- `chfs_loadvnode` handles type-specific reconstruction: directories load dirents; regular/socket nodes call `chfs_read_inode`; symlinks and device/fifo nodes read stored data payloads.
- VFS op table delegates some operations to UFS/genfs and marks unsupported file handles/snapshots.

Dependencies:
- NetBSD VFS, genfs, UFS compatibility, flash/EBH layer, CHFS scan/build helpers, GC thread.

Research notes:
- `chfs_sync` is a stub returning success.
- File handles and snapshots return `ENODEV`.
- Several comments mark debug-only includes and inherited UFS constants.
