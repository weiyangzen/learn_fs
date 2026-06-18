# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-1.c

This file implements unsquashfs support for Squashfs 1.0 images. It maps the v1 on-disk format into the shared unsquashfs operation interface.

Key functions:
- `read_block_list`: reads 16-bit v1 block sizes and expands them into current block-size flags.
- `read_inode`: parses v1 inodes and fills a shared `struct inode`.
- `squashfs_opendir`: reads v1/v2-style directory headers and entries.
- `read_filesystem_tables`: validates and reads v1 uid/gid tables.
- `read_super_1`: recognizes v1.0 superblocks and normalizes fields into `sBlk`.
- `squashfs_stat`: prints v1 filesystem details.

Version-specific behavior:
- v1 encodes uid through inode type grouping plus 4-bit uid index.
- gid value `15` means “same as uid”.
- No fragment table is used; `fragment_table_start` is set invalid.
- Symlinks/devices/FIFOs/sockets use filesystem creation time unless overridden.
- Compression is always gzip.

Corruption checks:
- Bounds-check uid/gid indexes.
- Rejects too many v1 uids/gids.
- Validates table ordering: inode table before directory table before uid/gid tables.
- Directory reading validates filename length, name characters, duplicate names, and sorts before duplicate checks.
