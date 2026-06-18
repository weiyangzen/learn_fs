# File Research: sources/os/linux/linux/fs/freevxfs/vxfs.h

Read status: complete, 257 lines.

Purpose: defines FreeVxFS superblock structures, endian helpers, inode mode constants, organization types, and superblock-private accessor macros.

Key content:
- Defines `VXFS_SUPER_MAGIC`, `VXFS_ROOT_INO`, and on-disk fixed-width endian-marked types `__fs16`, `__fs32`, `__fs64`.
- `struct vxfs_sb` models the VxFS disk superblock fields used by the driver, including block size, AU geometry, inode sizing, free counts, OLT location, and version fields.
- `struct vxfs_sb_info` stores mounted-state metadata: raw superblock buffer, fileset header inode, inode-list inodes, initial inode-list extent, OLT location/size, and byte order.
- `fs16_to_cpu()`, `fs32_to_cpu()`, and `fs64_to_cpu()` decode on-disk values according to detected byte order.
- Defines VxFS file type bits, internal structural inode types, organization types (`NONE`, `EXT4`, `IMMED`, `TYPED`), and predicate macros.

Important dependencies: Linux endian helpers, `struct super_block`, `struct buffer_head`, FreeVxFS inode/OLT readers.

Risk note: many on-disk structures are partial models of VxFS and comments state later/variant fields are omitted.
