# File Research: sources/os/linux/linux/fs/hfsplus/Makefile

Purpose: Defines HFS+ build objects and optional KUnit test object.

Key content:
- Builds `hfsplus.o` from superblock, options, inode, ioctl, extents, catalog, directory, B-tree, Unicode, wrapper, bitmap, partition, attributes, and xattr sources.
- Builds `unicode_test.o` under `CONFIG_HFSPLUS_KUNIT_TEST`.

Dependencies and integration:
- Reflects the HFS+ implementation split; the files in this research group are the B-tree, catalog, directory, extents, bitmap, and attributes core.
