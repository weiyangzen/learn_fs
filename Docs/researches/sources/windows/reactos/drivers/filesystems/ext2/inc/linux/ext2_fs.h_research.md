# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext2_fs.h

This Linux-derived header defines ext2 on-disk constants, structures, feature masks, directory layout, and kernel prototypes.

Major content:
- ext2 version/debug/preallocation constants.
- Special inode numbers, magic number, link limit, block/fragment sizing macros, inode-size and first-inode macros.
- ACL header and entry structures.
- `struct ext2_group_desc`.
- Direct/indirect block index constants and inode flags, including extents and huge-file flags.
- ioctl command constants.
- `struct ext2_inode`, including OS-dependent Linux/Hurd/Masix fields and extended inode size padding.
- Filesystem state, mount options, error behavior, default reserved uid/gid.
- `struct ext2_super_block` with classic ext2 dynamic revision fields.
- Feature flags and supported/unsupported feature masks.
- `struct ext2_dir_entry`, `struct ext2_dir_entry_2`, file-type enum, and directory record length macro.

Kernel-only declarations:
- Prototypes for ext2 block allocation, directory operations, inode operations, ioctl, superblock operations, and Linux VFS operation tables.

Role in this driver:
- Provides the ext2 on-disk contract used by the master driver header and by compatibility code.
- Also shares feature constants with ext3/ext4 code paths in this ReactOS port.

Notable constraints:
- User-mode feature-test macros assume an `EXT2_SB(sb)->s_es` layout, so callers must pass the expected wrapper, not only a raw superblock.
- Old Linux-era fields and feature masks are retained even when newer ext3/ext4 headers are also included.
