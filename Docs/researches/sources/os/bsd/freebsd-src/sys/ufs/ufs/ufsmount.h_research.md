# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufsmount.h

## Purpose
Defines the common UFS mount structure, mount arguments, mount flags, quota transition flags, filesystem type constants, and callback macros used by common UFS code to call UFS1/UFS2 or FFS-specific implementations.

## Key structures
- `struct ufs_args` contains the mount device path and export arguments.
- `struct ufsmount` is the UFS-specific mount-private state stored in `mount->mnt_data`.

## `struct ufsmount` contents
Major fields include:
- VFS and device bindings: `um_mountp`, `um_dev`, `um_cp`, `um_bo`, `um_odevvp`, `um_devvp`.
- Filesystem identity and geometry: `um_fstype`, `um_fs`, `um_nindir`, `um_bptrtodb`, `um_seqinc`, `um_bsize`, `um_maxsymlinklen`.
- Extended attributes and soft updates: `um_extattr`, `um_softdep`.
- Quota state: `um_quotas`, `um_cred`, `um_btime`, `um_itime`, `um_qflags`.
- Mount status and reporting: `um_flags`, full/integrity message timestamps and intervals.
- TRIM support state: inflight counts, totals, taskqueue, hash table, and hash mask.
- Operation callback table for allocation, block lookup, truncate, update, inode allocation/free, read-only test, snapshot gone hook, and block-number validation.

The lock legend documents fields as constant, protected by the UFS interlock, protected by quota-file locking, or requiring a VFS mount reference.

## Operation macros
The header defines common dispatch macros:
- `UFS_BALLOC`, `UFS_BLKATOFF`, `UFS_TRUNCATE`, `UFS_UPDATE`.
- `UFS_VALLOC`, `UFS_VFREE`, `UFS_IFREE`.
- `UFS_RDONLY`, `UFS_SNAPGONE`, `UFS_CHECK_BLKNO`.
- `VFSTOUFS` and `UFSTOVFS` for mount conversion.
- `UFS_LOCK`, `UFS_UNLOCK`, `UFS_MTX`.

These macros are used throughout the common UFS source files so shared code can call filesystem-specific implementations without directly knowing whether it is operating on UFS1, UFS2, or a specific FFS backend.

## Constants and flags
- Filesystem types: `UFS1`, `UFS2`.
- Mount flags: `UM_CANDELETE`, `UM_WRITESUSPENDED`, `UM_CANSPEEDUP`, `UM_FSFAIL_CLEANUP`.
- Quota state flags: `QTF_OPENING`, `QTF_CLOSING`, `QTF_64BIT`.
- Geometry helpers: `MNINDIR`, `blkptrtodb`, `is_sequential`.
- `OFSFMT(vp)` detects old filesystem directory format based on `um_maxsymlinklen`.

## Research notes
This header is the abstraction point that lets common UFS vnode, lookup, quota, inactive, and VFS code remain independent of lower-level allocation and update mechanics. Correct use of its lock annotations and callback macros is necessary to understand the rest of the UFS implementation.
