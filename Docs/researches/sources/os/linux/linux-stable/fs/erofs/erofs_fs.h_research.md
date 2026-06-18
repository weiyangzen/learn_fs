# File Research: sources/os/linux/linux-stable/fs/erofs/erofs_fs.h

## Summary
Defines the EROFS on-disk format.

## Main Contents
- Superblock, device slot, compact inode, extended inode, xattr, chunk, dirent, compressed map, lcluster, and extent structures.
- Compatible and incompatible feature flags.
- Datalayout, inode-format, xattr, compression algorithm, and compressed-index constants.
- Compile-time layout assertions.

## Important Details
EROFS supports flat, inline, compressed full/compact, and chunk-based inode layouts. Optional features include 48-bit addressing, device tables, metabox metadata compression, fragments, dedupe, long xattr prefixes, and multiple compression algorithms.

## Risks
This header is ABI-like on-disk format definition. Any structure size or bit assignment change would affect filesystem compatibility; `erofs_check_ondisk_layout_definitions()` enforces key layout sizes.
