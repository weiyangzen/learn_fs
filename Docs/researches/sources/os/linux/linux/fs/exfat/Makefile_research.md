# File Research: sources/os/linux/linux/fs/exfat/Makefile

## Purpose
Builds the Linux exFAT filesystem object when `CONFIG_EXFAT_FS` is enabled.

## Main Interfaces
- `obj-$(CONFIG_EXFAT_FS) += exfat.o`
- `exfat-y` composes `exfat.o` from `inode.o`, `namei.o`, `dir.o`, `super.o`, `fatent.o`, `cache.o`, `nls.o`, `misc.o`, `file.o`, and `balloc.o`.

## Dependencies
The Makefile reveals the driver’s internal layering: superblock/mount logic in `super.o`; inode/page-cache mapping in `inode.o`; namespace operations in `namei.o`; directory entry handling in `dir.o`; allocation bitmap and FAT chain management in `balloc.o` and `fatent.o`; cluster cache in `cache.o`; charset/upcase support in `nls.o`; shared helpers in `misc.o`; and regular file operations in `file.o`.

## Risks
Any new exFAT implementation file must be added here to participate in the monolithic `exfat.o` module.
