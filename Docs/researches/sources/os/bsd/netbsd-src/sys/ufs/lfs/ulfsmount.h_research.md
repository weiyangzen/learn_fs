# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfsmount.h

This header defines the ULFS-specific mount-private structure used by LFS’s UFS-derived layer.

Key contents:
- `struct ulfsmount` stores the backing `struct mount`, filesystem type, `struct lfs *`, extended-attribute state, and quota state.
- Supports quota1 and quota2 through a union of per-mount quota timers/flags or quota2 block-size metadata.
- Defines mount flags such as `ULFS_NEEDSWAP`, `ULFS_QUOTA`, and `ULFS_QUOTA2`.
- Defines filesystem type constants `ULFS1` and `ULFS2`.
- Provides `VFSTOULFS(mp)` and bmap helper macros `MNINDIR` and `blkptrtodb`.

Notable dependency:
- Includes LFS versions of extattr and quota-common headers, making this the central mount bridge for ULFS vnode, quota, and byte-swap logic.
