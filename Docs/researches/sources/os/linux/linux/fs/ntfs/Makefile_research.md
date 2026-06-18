# File Research: sources/os/linux/linux/fs/ntfs/Makefile

## Role

This Makefile builds the Linux NTFS filesystem module/object set.

## Objects

`obj-$(CONFIG_NTFS_FS)` builds `ntfs.o`.

The `ntfs-y` list includes address-space operations, attributes, collation, directory handling, file handling, indexes, inode/MFT logic, runlists, superblock code, unicode/upcase support, attrlists, extended attributes, bitmap/LCN allocation, logfile, reparse, compression, iomap, debug, sysctl, quota, object id, and block-device I/O modules.

When `CONFIG_NTFS_DEBUG` is enabled, `-DDEBUG` is added.

## Design Notes

The Makefile shows NTFS as one monolithic filesystem module split internally by metadata, namespace, allocation, I/O, and support subsystems.
