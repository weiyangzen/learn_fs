# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/ext2_fs.h

This header defines classic ext2 on-disk constants, structures, and feature macros.

Core contents:
- Ext2 version, special inode numbers, magic, block/fragment sizing macros, and group descriptor layout.
- ACL, directory indexing, group descriptor, inode, superblock, and directory entry structures.
- Inode flags, mount flags, filesystem state/error values, OS creator codes, revision levels, and feature bits.
- Directory entry file type constants and record-length macros.
- Kernel-only declarations retained under `#ifdef __KERNEL__`.

Important behavior:
- User-mode macros treat the passed object as an ext2 superblock directly.
- `EXT2_INODE_SIZE` and `EXT2_FIRST_INO` depend on revision level.
- Supported feature masks are old ext2/ext3-era values, with incompatible support limited to filetype.

Risk points:
- This is a legacy ext2 header and does not include ext4-era structures/features.
- Multi-byte disk fields are represented as host integer types; ReactOS targets little-endian behavior.
- Kernel-only declarations are irrelevant for this user-mode formatter but remain in the file.
