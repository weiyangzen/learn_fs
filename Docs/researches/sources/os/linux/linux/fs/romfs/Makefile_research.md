# File Research: sources/os/linux/linux/fs/romfs/Makefile

## Purpose
Build rules for the Linux ROMFS filesystem module/built-in object.

## Build Behavior
- `obj-$(CONFIG_ROMFS_FS) += romfs.o`: builds ROMFS when configured.
- `romfs-y := storage.o super.o`: core ROMFS object always includes storage access and superblock/inode logic.
- `romfs-$(CONFIG_ROMFS_ON_MTD) += mmap-nommu.o` only when `CONFIG_MMU` is not `y`.

## Integration
The Makefile mirrors Kconfig:
- `storage.o` handles block and/or MTD reads according to `ROMFS_ON_BLOCK` and `ROMFS_ON_MTD`.
- `mmap-nommu.o` is included only for NOMMU MTD direct-map support.

## Research Notes
This is a minimal feature-gated build file. Direct mmap support is intentionally absent on MMU builds.
