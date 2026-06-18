# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufsmount.h

Read completely: 94 lines.

Defines UFS-specific mount state and mount-level helper macros.

Core definitions:
- `struct ufsmount` stores the generic mount pointer, device id, device vnode, filesystem type, FFS/ext2 superblock pointer union, quota vnodes/credentials, indirect-pointer geometry, sequential block increment, quota grace times, quota flags, export data, saved max file size, and max short-symlink length.
- Defines mount filesystem type constants `UM_UFS1`, `UM_UFS2`, and `UM_EXT2FS`.
- Defines quota transition flags `QTF_OPENING` and `QTF_CLOSING`.
- `VFSTOUFS()` converts generic mount data to `struct ufsmount`.
- `MNINDIR()`, `blkptrtodb()`, and `is_sequential()` provide block mapping helpers used by bmap and clustered I/O.

Integration and risks:
- The superblock union and `um_fstype` drive UFS1/UFS2/ext2 field interpretation across the subsystem.
- Quota arrays must match `MAXQUOTAS`.
- Block pointer conversion macros assume mount geometry was initialized correctly at mount time.
