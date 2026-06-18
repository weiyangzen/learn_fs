# File Research: sources/os/linux/linux/fs/omfs/omfs_fs.h

OMFS on-disk format definitions.

Key contents:
- Defines filesystem magic values, inode type characters, name length, fixed offsets, checksum constants, and size limits.
- `OMFS_MAGIC` identifies the superblock; `OMFS_IMAGIC` identifies inode/header records.
- `OMFS_DIR_START`, `OMFS_EXTENT_START`, and `OMFS_EXTENT_CONT` define where directory hash buckets and extent tables begin inside system blocks.
- Maximums include `OMFS_NAMELEN` 256, max block size 8192, max cluster size 8, and max blocks `1 << 31`.

On-disk structures:
- `struct omfs_super_block`: primary superblock with root block pointer, total blocks, magic, block size, mirror count, and system block size.
- `struct omfs_header`: shared metadata header containing self block, body size, CRC, version, type, magic, XOR checksum, and padding.
- `struct omfs_root_block`: root metadata containing total blocks, root directory block, bitmap block, block size, cluster size, mirror count, and volume name.
- `struct omfs_inode`: file/directory inode metadata with parent, sibling chain pointer, ctime, type, name, and file size.
- `struct omfs_extent_entry`: start cluster plus block count.
- `struct omfs_extent`: extent table header with next continuation pointer, extent count, fill field, and flexible array of extent entries.

Format conventions:
- Multi-byte fields are big-endian.
- `~0ULL` is used as a sentinel for absent bitmap, end-of-chain sibling, end-of-extent table, and empty bucket pointers.
- Directories and files share the inode structure; type-specific payload starts at fixed offsets inside the same system block.
