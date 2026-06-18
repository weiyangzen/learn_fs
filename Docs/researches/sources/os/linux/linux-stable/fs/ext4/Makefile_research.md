# File Research: sources/os/linux/linux-stable/fs/ext4/Makefile

## Purpose

Builds the ext4 filesystem module/object set.

## Main Build Rules

- `obj-$(CONFIG_EXT4_FS) += ext4.o`
- `ext4-y` includes core ext4 implementation files:
  - allocation, bitmaps, block validity, directories, journaling, extents, file operations, fsmap, fsync, hashing, inode allocation, indirect blocks, inline data, inode logic, ioctls, multiblock allocation, migration, MMP, move extent, namei, page I/O, readpage, resize, superblock, symlink, sysfs, xattrs, trusted/user xattrs, fast commit, and orphan handling.
- `ext4-$(CONFIG_EXT4_FS_POSIX_ACL) += acl.o`
- `ext4-$(CONFIG_EXT4_FS_SECURITY) += xattr_security.o`
- `obj-$(CONFIG_EXT4_KUNIT_TESTS) += ext4-test.o`
- `ext4-$(CONFIG_FS_VERITY) += verity.o`
- `ext4-$(CONFIG_FS_ENCRYPTION) += crypto.o`

## Test Objects

`ext4-test-objs` includes:

- `inode-test.o`
- `mballoc-test.o`
- `extents-test.o`

## Research Notes

The Makefile shows ext4 is a broad monolithic filesystem object with feature-gated additions. The files in this research group cover early entries in `ext4-y` plus optional ACL/encryption support.
