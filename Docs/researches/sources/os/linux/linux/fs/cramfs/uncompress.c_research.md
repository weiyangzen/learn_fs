# File Research: sources/os/linux/linux/fs/cramfs/uncompress.c

## Purpose
Wraps zlib inflate for cramfs block decompression with shared global stream initialization and teardown.

## Main Elements
- Static zlib `stream` and `initialized` reference count.
- `cramfs_uncompress_block()`: resets the stream, inflates one compressed block into the destination, reports zlib errors, and returns decompressed byte count or `-EIO`.
- `cramfs_uncompress_init()`: allocates zlib workspace with `vmalloc()` and initializes inflate state on first user.
- `cramfs_uncompress_exit()`: ends inflate and frees workspace on final user.

## Dependencies And Integration
Used by `cramfs_read_folio()` in `inode.c`. The global stream is serialized by `read_mutex` in the caller.

## Risk Notes
The file explicitly notes decompression is single-threaded. Reset failure attempts to end and reinitialize the zlib stream, but decompression errors still abort the folio read.
