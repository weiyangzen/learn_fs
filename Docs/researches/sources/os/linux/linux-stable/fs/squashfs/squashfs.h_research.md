# File Research: sources/os/linux/linux-stable/fs/squashfs/squashfs.h

## Summary
Central internal Squashfs header declaring cross-file APIs, operations tables, trace/error macros, and decompressor-thread operations.

## Main Contents
- Logging macros `TRACE`, `ERROR`, and `WARNING`.
- `SQUASHFS_READ_PAGES` build-time behavior for the intermediate data cache.
- Prototypes for block I/O, caches, decompressor setup, export, fragments, file reads, ids, inodes, xattrs, directories, symlinks, and operations tables.
- `struct squashfs_decompressor_thread_ops`.

## Important Details
This header is the link point between conditional files selected by the Makefile. `squashfs_readpage_block()` is provided by either `file_cache.c` or `file_direct.c`, and decompressor thread ops are provided according to Kconfig.

## Risks
Because this is the shared internal ABI, signature changes require coordinated edits across many Squashfs files and compression wrappers.
