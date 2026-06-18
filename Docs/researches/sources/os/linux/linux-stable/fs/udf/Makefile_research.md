# File Research: sources/os/linux/linux-stable/fs/udf/Makefile

## Summary
Builds the UDF filesystem object when `CONFIG_UDF_FS` is enabled.

## Main Responsibilities
- Adds `udf.o` for built-in or module builds.
- Links the UDF implementation from allocation, directory, file, inode, low-level, name lookup, partition, superblock, truncation, symlink, misc, time, and unicode sources.

## Build Contents
`udf-objs` includes:
`balloc.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `lowlevel.o`, `namei.o`, `partition.o`, `super.o`, `truncate.o`, `symlink.o`, `directory.o`, `misc.o`, `udftime.o`, and `unicode.o`.

## Risks
There is no conditional source selection here; Kconfig dependencies must provide all external support required by every object.
