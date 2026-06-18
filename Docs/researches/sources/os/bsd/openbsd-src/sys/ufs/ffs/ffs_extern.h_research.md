# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_extern.h

Public internal header for FFS kernel routines, vop tables, sysctl IDs, and pools.

Contents:
- Defines FFS sysctl IDs, mostly legacy/softdep names plus active dirhash settings.
- Defines `FFS_NAMES` sysctl name table.
- Forward-declares kernel structs used by prototypes.
- Exports `ffs_vops`, `ffs_specvops`, and `ffs_fifovops`.
- Declares allocation, block allocation, inode update/truncate, helper, VFS, vnode, and softdep-related functions.
- Exports inode and dinode pools.

Important role:
- This is the API boundary between FFS implementation files and shared UFS code.
- FFS2-specific declarations are guarded by `#ifdef FFS2`.
- The prototypes expose the major layering: allocation, balloc, inode ops, subr helpers, vfsops, and vnops.
