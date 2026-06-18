# File Research: sources/os/linux/linux-stable/fs/squashfs/file_cache.c

## Summary
Provides the file data read implementation for `CONFIG_SQUASHFS_FILE_CACHE`.

## Key APIs
- `squashfs_readpage_block()`.

## Important Behavior
Reads a compressed data block through `squashfs_get_datablock()`, which uses the generic Squashfs cache as an intermediate decompression buffer, then calls `squashfs_copy_cache()` to copy bytes into page-cache folios.

## Risks
This path adds an extra copy but avoids direct decompression into page-cache pages. Cache entry lifetime is simple but still requires `squashfs_cache_put()` after copy/error handling.
