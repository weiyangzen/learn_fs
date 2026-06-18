# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_compr.h

This header defines NTFS compression geometry and exports decompression helpers. `NTFS_COMPBLOCK_SIZE` is `0x1000` bytes and `NTFS_COMPUNIT_CL` is 16 clusters.

Exported functions are `ntfs_uncompblock()` for one compression block and `ntfs_uncompunit()` for a compression unit.

Research notes: callers need `struct ntfsmount` and the cluster conversion macros from `ntfs.h`; this header is intentionally small and only covers decompression.
