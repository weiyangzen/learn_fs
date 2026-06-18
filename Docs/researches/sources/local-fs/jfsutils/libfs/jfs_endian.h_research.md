# File Research: sources/local-fs/jfsutils/libfs/jfs_endian.h

## Purpose
Declares or no-ops the JFS byte-swapping API depending on host endianness.

## Big-Endian Behavior
Declares all swap functions implemented in `jfs_endian.c`, including map, inode, tree, superblock, journal, and fsck workspace swaps. Also defines:
- `ujfs_swap_inoext()`: inline loop over `INOSPEREXT` dinodes.
- `swap_multiple(swap_func, ptr, num)`: helper macro to swap arrays.

## Little-Endian Behavior
All swap functions and `swap_multiple` become empty `do {} while (0)` macros.

## Dependencies
Includes JFS type, byteorder, superblock, dmap, imap, dinode, log manager, and fsck workspace headers.

## Notes
This header centralizes endianness handling for libfs. Callers can invoke swap helpers unconditionally and rely on compile-time no-ops on the common little-endian path.
