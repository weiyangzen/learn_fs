# File Research: sources/os/linux/linux-stable/fs/fat/Makefile

## Purpose
`Makefile` defines build targets for Linux FAT-family filesystem modules/objects.

## Build Rules
- `obj-$(CONFIG_FAT_FS) += fat.o`
- `obj-$(CONFIG_VFAT_FS) += vfat.o`
- `obj-$(CONFIG_MSDOS_FS) += msdos.o`
- `obj-$(CONFIG_FAT_KUNIT_TEST) += fat_test.o`

## Object Composition
- `fat-y` is built from shared FAT core files:
  - `cache.o`
  - `dir.o`
  - `fatent.o`
  - `file.o`
  - `inode.o`
  - `misc.o`
  - `nfs.o`
- `vfat-y` is built from `namei_vfat.o`.
- `msdos-y` is built from `namei_msdos.o`.

## Dependencies
This file directly reflects the options declared in `fs/fat/Kconfig`, mapping selected kernel config symbols to core, VFAT, MSDOS, and KUnit test build products.
