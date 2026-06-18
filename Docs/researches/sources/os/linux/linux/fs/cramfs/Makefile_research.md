# File Research: sources/os/linux/linux/fs/cramfs/Makefile

## Purpose
Builds the cramfs module or built-in filesystem object.

## Main Elements
- `obj-$(CONFIG_CRAMFS) += cramfs.o`.
- Composite objects: `inode.o` and `uncompress.o`.

## Dependencies And Integration
Links VFS/image handling with zlib decompression wrappers.

## Risk Notes
No conditional object split is used for blockdev versus MTD; feature differences are compiled through Kconfig conditionals in `inode.c`.
