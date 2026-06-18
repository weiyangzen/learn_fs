# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_bswap.h

## Scope

Defines ULFS/LFS byte-order access helpers for swapped-endian filesystem support.

## APIs And Behavior

- `ULFS_MPNEEDSWAP()`, `ULFS_FSNEEDSWAP()`, and `ULFS_IPNEEDSWAP()` report whether mount, filesystem, or inode fields require byte swapping when `LFS_EI` is enabled.
- `ulfs_rw16()`, `ulfs_rw32()`, and `ulfs_rw64()` return byte-swapped or unchanged values.
- `ulfs_add16()`, `ulfs_add32()`, and `ulfs_add64()` read, add, and write back values in on-disk byte order.

## State And Dependencies

The header depends on `sys/bswap.h` and conditional kernel/endian support. Without `LFS_EI`, swap checks compile to constant false and read/write helpers return unchanged values.

## Risks And Invariants

All on-disk dinode, directory, and block-pointer accessors relying on these macros must pass the correct swap flag. Builds without endian-independent LFS intentionally cannot mount swapped filesystems.
