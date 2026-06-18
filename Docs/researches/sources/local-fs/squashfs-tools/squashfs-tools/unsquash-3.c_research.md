# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-3.c

This file implements unsquashfs support for Squashfs 3.0 and 3.1 images.

Key functions:
- `salloc_index_table`: scratch allocation for swapped index tables.
- `read_block_list`: reads v3 block lists.
- `read_fragment_table` and `read_fragment`: handle v3 64-bit fragment indexes and entries.
- `read_inode`: parses v3 inode variants, including large regular files.
- `squashfs_opendir`: reads v3 directories.
- `parse_exports_table`: validates and steps over the export lookup table.
- `read_filesystem_tables`: validates old uid/gid, export, fragment, directory, and inode tables.
- `read_super_3`: reads, endian-swaps if needed, recognizes v3 superblocks, and normalizes `sBlk`.
- `squashfs_stat`: prints v3 metadata.

Version-specific behavior:
- v3 adds real inode numbers and optional export lookup table support.
- Directory data size treats `3` as empty and subtracts `3` during parsing.
- Large regular files support 64-bit sizes.
- Regular files mark `i.sparse = 1`.
- Compression is always gzip.

Corruption checks:
- Rejects inode type outside `1..9`, inode number zero, and inode number greater than superblock inode count.
- Validates negative large file sizes.
- Validates table ordering and fragment/export index lengths.
- Checks directory sortedness and duplicate names.
