# File Research: sources/os/linux/linux/fs/cramfs/internal.h

## Purpose
Declares cramfs decompression interfaces used by the filesystem implementation.

## Main Elements
- `cramfs_uncompress_block()`: decompress one block.
- `cramfs_uncompress_init()`: initialize shared zlib state.
- `cramfs_uncompress_exit()`: release shared zlib state.

## Dependencies And Integration
Included by `inode.c` and implemented by `uncompress.c`.

## Risk Notes
The interface hides the fact that decompression state is global and single-threaded; callers must serialize around it.
