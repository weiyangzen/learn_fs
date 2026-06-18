# File Research: sources/os/linux/linux-stable/fs/ext4/Kconfig

## Purpose

Defines kernel configuration options for building and enabling ext4 functionality.

## Main Options

- `EXT4_FS`: tristate ext4 filesystem support.
- `EXT4_USE_FOR_EXT2`: allows ext4 driver code to mount ext2 filesystems when the ext2 driver is not built.
- `EXT4_FS_POSIX_ACL`: enables ext4 POSIX ACL support and selects `FS_POSIX_ACL`.
- `EXT4_FS_SECURITY`: enables ext4 security labels through xattrs.
- `EXT4_DEBUG`: enables runtime ext4 debugging messages through dynamic debug.
- `EXT4_KUNIT_TESTS`: builds ext4 KUnit tests.

## Dependencies and Selections

`EXT4_FS` selects:

- `BUFFER_HEAD`
- `JBD2`
- `CRC16`
- `CRC32`
- `FS_IOMAP`
- `FS_ENCRYPTION_ALGS` when `FS_ENCRYPTION` is enabled

`EXT4_KUNIT_TESTS` depends on `EXT4_FS && KUNIT` and defaults to `KUNIT_ALL_TESTS`.

## Research Notes

The configuration describes ext4 as the successor to ext3 and notes it can mount ext3-compatible filesystems. Optional feature blocks map directly to conditional objects in the Makefile, especially ACL, security xattrs, encryption, verity, and tests.
