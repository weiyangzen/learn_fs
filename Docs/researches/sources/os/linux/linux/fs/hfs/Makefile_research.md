# File Research: sources/os/linux/linux/fs/hfs/Makefile

## Scope

This Makefile defines the object composition for the Linux HFS filesystem module/built-in target and its KUnit test target.

## Build Rules

- `obj-$(CONFIG_HFS_FS) += hfs.o` builds the aggregate HFS object when the filesystem is enabled.
- `hfs-objs` includes bitmap, B-tree find/node/record/tree, catalog, directory, extent, inode, attr, MDB, partition table, string, super, sysdep, and transaction objects.
- `obj-$(CONFIG_HFS_KUNIT_TEST) += string_test.o` builds the string KUnit tests when configured.

## Dependencies

The object list shows that the files in this group (`attr.c`, `bfind.c`, `bitmap.c`, `bnode.c`) are core components of the single `hfs.o` target.
