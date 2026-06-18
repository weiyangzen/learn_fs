# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-4.c

This file implements unsquashfs support for current Squashfs 4.0 images.

Key functions:
- `read_block_list`: reads and endian-converts file block sizes.
- `read_fragment_table` and `read_fragment`: read and serve fragment entries.
- `read_inode`: parses all v4 inode variants, including long inode forms with xattrs.
- `squashfs_opendir`: reads v4 directories.
- `read_id_table`: reads metadata-block indexed id table.
- `parse_exports_table`: validates export lookup table index.
- `read_filesystem_tables`: validates and reads xattrs, ids, exports, fragments, and table boundaries.
- `read_super_4`: recognizes normal and streamed v4 superblocks, handles endian conversion, and selects compressor by id.
- `read_xattr_ids` and `squashfs_stat`: report xattr and filesystem stats.

Version-specific behavior:
- Supports xattrs, id table compression, compressor options, sparse long regular files, and long inode types for xattr-bearing objects.
- Streamed Squashfs magic causes the reader to seek to the final superblock.
- Uses `SQUASHFS_INSWAP_*` macros, making endian handling host-dependent.
- `no_xattrs` can suppress xattr use by invalidating `xattr_id_table_start`.

Corruption checks:
- Validates uid/gid indexes against `no_ids`, inode type `1..14`, inode numbers, symlink size, fragment indexes, id count, table ordering, and negative file sizes.
- Ensures id count is nonzero and not more than twice inode count.
- Fragment count cannot exceed inode count.
