# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs.h

This is the main Linux-derived ext3/ext4 format header for the driver. It defines ext3 on-disk layout plus selected ext4 group descriptor, feature, inode, directory, htree, and MMP structures.

Major content:
- ext3 reservation constants, special inode numbers, link limit, block/fragment size macros.
- `struct ext3_group_desc` and extended `struct ext4_group_desc`.
- `struct flex_groups` and ext4 block group flags.
- ext3/ext4 descriptor sizing and block group macros.
- ext3 and ext4 inode flags, user-visible/modifiable masks, and dynamic inode state bits.
- online resize input/data structures and ioctl constants.
- mount option structure and mount-option bit definitions.
- `struct ext3_inode`, including high size/block/ACL fields and extra timestamp fields.
- `struct ext3_super_block`, extended with journal, htree, descriptor size, 64-bit block count, extra inode size, MMP, RAID, and flex-bg fields.
- `EXT3_SB`, `EXT3_I`, and `ext3_valid_inum` for kernel builds.
- ext3/ext4 feature-test, set, clear, supported-feature, and unsupported-feature constants.
- Directory entry structures, file type constants, Lustre dirent extension helpers, record-length conversion helpers, and htree hash constants.
- Kernel-only htree support structures, `ext3_iloc`, `dir_private_info`, group-first-block helper, MMP structure, xattr ctime flag, and `ext3_match`.

Role:
- Bridges ext3 and partial ext4 compatibility for Ext2Fsd, especially journal-aware metadata, indexed directories, extents flags, large/huge files, and group descriptor checksums.

Notable risks:
- `EXT4_HTREE_EOF_64BIT` appears to be missing a closing parenthesis in the macro definition.
- Many ext4 feature flags are declared, but supported masks only include a subset, so mount/write policy must reject or degrade unsupported volumes correctly.
- `ext3_match` uses `_strnicmp`, making name matching case-insensitive in this port.
