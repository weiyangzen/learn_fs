# File Research: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_fs.h

This is the primary Squashfs 4.0 on-disk format header. It defines current filesystem constants, flag encodings, inode/address helpers, table sizing macros, compression ids, and all v4 disk structures.

Key contents:
- Filesystem identity: `SQUASHFS_MAGIC`, streamed variants, major/minor `4:0`.
- Metadata sizing: 8192-byte metadata blocks, default 128 KiB data blocks, max 1 MiB block setting.
- Flag bits and helpers for uncompressed inodes/data/fragments/xattrs/ids, fragments, duplicates, exportability, compressor options, and xattr disabling.
- Inode address helpers: `SQUASHFS_INODE_BLK`, `SQUASHFS_INODE_OFFSET`, `SQUASHFS_MKINODE`.
- Table sizing macros for fragments, lookup/export table, id table, and xattr id table.
- Current structures: `squashfs_super_block`, inode variants, directory entries, fragment entries, xattr entries, and xattr table.

Important behavior:
- v4 inode structures separate “short” and “long” forms; long forms carry fields such as xattr id, sparse count, larger size, or nlink.
- Fragment, id, lookup, and xattr tables use metadata-block indexed tables whose byte counts are calculated here.
- Compression ids map on-disk numeric values to compressor implementations: gzip/zlib, LZMA, LZO, XZ, LZ4, ZSTD.

Corruption-sensitive details:
- Many readers use these macros for allocation sizes. Overflow assumptions matter when converting counts to bytes.
- `SQUASHFS_NAME_LEN` is 256, and code treats names with size >= this as corrupted.
