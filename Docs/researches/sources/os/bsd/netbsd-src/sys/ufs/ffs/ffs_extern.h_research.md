# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_extern.h

This header is the main external interface for NetBSD FFS implementation files. It declares sysctl IDs, kernel pools, vnode/VFS entry points, allocation and block I/O helpers, snapshot hooks, WAPBL hooks, Apple UFS helpers, byte-swap helpers, and common FFS subroutines.

Key responsibilities:
- Define FFS sysctl identifiers.
- Publish kernel-only FFS APIs across allocation, block allocation, inode update/truncate, VFS operations, vnode operations, extattrs, snapshots, and WAPBL.
- Publish non-kernel-safe helpers for Apple UFS metadata and byte swapping.
- Define `FFS_NOBLK` and `FFS_ITIMES`.

Important declarations:
- Allocation: `ffs_alloc`, `ffs_realloccg`, `ffs_valloc`, `ffs_blkalloc`, `ffs_blkfree`, `ffs_vfree`, discard helpers, snapshot-aware free helpers.
- Block allocation: `ffs_balloc`.
- Inode lifecycle: `ffs_update`, `ffs_truncate`, `ffs_itimes`.
- VFS: `VFS_PROTOS(ffs)`, `ffs_reload`, `ffs_mountfs`, `ffs_flushfiles`, `ffs_sbupdate`, `ffs_cgupdate`.
- Vnode ops: `ffs_read`, `ffs_write`, `ffs_bufio`, `ffs_bufrd`, `ffs_bufwr`, `ffs_fsync`, `ffs_spec_fsync`, `ffs_reclaim`, `ffs_full_fsync`, page/lock helpers.
- Extended attributes: `ffs_openextattr`, `ffs_closeextattr`, `ffs_getextattr`, `ffs_setextattr`, `ffs_listextattr`, `ffs_deleteextattr`, `ffsext_strategy`.
- Snapshots: init/fini/create/mount/unmount/read/remove/block-free hooks.
- WAPBL: replay/start/stop/sync/abort hooks.
- Byte swapping: `ffs_sb_swap`, dinode swaps, csum swaps, cylinder-group swap.
- Support routines: `ffs_load_inode`, `ffs_getblk`, fragment/block/cluster accounting.

Important interactions:
- Centralizes ABI between `ffs_*.c`, shared UFS code, and kernel VFS registration.
- Exposes `ffs_vnodeop_p`, `ffs_specop_p`, and `ffs_fifoop_p` operation vectors used by vnode initialization.

Notable behavior and risks:
- Many declarations are gated on `_KERNEL`; userland tools still get byte-swap and some subroutine declarations.
- `FFS_ITIMES` loops while inode time flags remain set, so callers rely on `ffs_itimes` clearing the pending flags.
