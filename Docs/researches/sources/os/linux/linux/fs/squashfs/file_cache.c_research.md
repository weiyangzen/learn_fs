# File Research: sources/os/linux/linux/fs/squashfs/file_cache.c

Implements the intermediate-buffer file-data read strategy.

`squashfs_readpage_block()` reads a compressed datablock through the generic data cache, then copies the decompressed buffer into page-cache folios via `squashfs_copy_cache()`.

This path favors reuse of existing cache/copy infrastructure but adds a memcpy compared with direct mode.
