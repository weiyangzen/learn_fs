# File Research: sources/os/linux/linux-stable/fs/exfat/Makefile

This Makefile wires the exFAT filesystem into the kernel build.

Key elements:
- Builds `exfat.o` when `CONFIG_EXFAT_FS` is enabled.
- `exfat-y` is composed from:
  - `inode.o`
  - `namei.o`
  - `dir.o`
  - `super.o`
  - `fatent.o`
  - `cache.o`
  - `nls.o`
  - `misc.o`
  - `file.o`
  - `balloc.o`

Important dependency meaning:
- The file list reflects the subsystem split: inode/address-space mapping, VFS name operations, directory entry handling, superblock/mount support, FAT and bitmap allocation, cluster cache, Unicode/NLS conversion, utility routines, regular file operations, and allocation bitmap management.

Scope note:
- `super.c` is built here but is outside this group; the files in this group depend on its mount-time initialization of `struct exfat_sb_info`, root inode setup, options, volume flags, and teardown paths.
