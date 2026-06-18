# File Research: sources/os/linux/linux-stable/fs/ntfs/Makefile

## Summary
Build rules for the NTFS kernel module.

## Contents
Builds `ntfs.o` when `CONFIG_NTFS_FS` is enabled and lists the component objects for address-space operations, attributes, collation, directories, files, indexes, inode/MFT handling, runlists, superblock, Unicode, allocation, logs, reparse points, compression, iomap, quota, object IDs, and block-device I/O.

## Important Details
`CONFIG_NTFS_DEBUG` adds `-DDEBUG` through `ccflags`.

## Risks
The object list defines the module composition; omitting any of these pieces would break major filesystem functionality such as metadata lookup, compression, or iomap I/O.
