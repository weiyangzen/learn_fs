# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-2.c

This file implements unsquashfs support for Squashfs 2.0 and 2.1 images.

Key functions:
- `read_block_list`: reads 32-bit block-size list entries.
- `read_fragment_table`: reads v2 fragment index/table data.
- `read_fragment`: returns fragment start and size.
- `read_inode`: parses v2 inode variants.
- `squashfs_opendir`: reads v2 directories.
- `read_filesystem_tables`: validates uid/gid, fragment, directory, and inode table layout.
- `read_super_2`: recognizes v2 superblocks and normalizes `sBlk`.
- `squashfs_stat`: prints v2 feature summary.

Version-specific behavior:
- Supports fragments, unlike v1.
- v2.0 may need directory sorting; `needs_sorting` is set for minor 0.
- gid value `SQUASHFS_GUIDS` means “same as uid”.
- Compression is always gzip.
- xattrs are absent and marked invalid.

Corruption checks:
- Fragment table index byte count must match table boundaries.
- Fragment count cannot exceed inode count.
- Directory count, filename length, and names are validated.
- Sortedness/duplicates are checked, with different diagnostics depending on whether sorting was expected.
