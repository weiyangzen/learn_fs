# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/native.c

Tiny endianness helper file. It exports `ext2fs_native_flag()` returning `EXT2_FLAG_SWAP_BYTES` on big-endian builds and `0` on little-endian builds.

Callers can use this to determine whether on-disk ext metadata needs byte swapping relative to the host.
