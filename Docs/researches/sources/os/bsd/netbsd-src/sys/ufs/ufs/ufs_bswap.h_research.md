# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_bswap.h

This header provides UFS endian-conversion helpers.

Key contents:
- Defines mount/filesystem/inode byte-swap predicates when `FFS_EI` is enabled.
- Provides inline `ufs_rw16`, `ufs_rw32`, and `ufs_rw64`.
- In non-swapping builds, helpers return inputs unchanged.
- Defines add-and-reswap helpers `ufs_add16`, `ufs_add32`, and `ufs_add64`.

Role:
- Centralizes endian-independent access for UFS metadata and quota/extattr support.
