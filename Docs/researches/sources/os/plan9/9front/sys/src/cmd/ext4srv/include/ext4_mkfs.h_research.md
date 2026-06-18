# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_mkfs.h

Mkfs parameter and auxiliary-layout header.

Key behavior:
- `ext4_mkfs_info` stores requested/derived filesystem length, block size, blocks per group, inodes per group, inode size/count, journal size, feature masks, reserved descriptor blocks, descriptor size, UUID, journal flag, and label.
- `fs_aux_info` stores allocated superblock and group descriptor buffers plus derived layout values such as first data block, block count, inode table blocks, group count, descriptor blocks, default inode flags, and indirect block geometry.
- Declares aux-info creation/release, superblock writing, existing-filesystem info readback, and `ext4_mkfs`.

Notable dependencies:
- Includes `ext4_blockdev.h` and `ext4_fs.h`.
- Implemented by `ext4_mkfs.c`.

Research notes:
- `fs_aux_info::xattrs` is present but unused in the read implementation.
