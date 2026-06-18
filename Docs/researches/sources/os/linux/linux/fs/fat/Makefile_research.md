# File Research: sources/os/linux/linux/fs/fat/Makefile

Defines object composition for Linux FAT-family filesystem modules.

Key behavior:
- Builds `fat.o` when `CONFIG_FAT_FS` is enabled.
- Builds `vfat.o` when `CONFIG_VFAT_FS` is enabled.
- Builds `msdos.o` when `CONFIG_MSDOS_FS` is enabled.
- Composes the common FAT object from:
  - `cache.o`
  - `dir.o`
  - `fatent.o`
  - `file.o`
  - `inode.o`
  - `misc.o`
  - `nfs.o`
- Composes VFAT from `namei_vfat.o`.
- Composes MSDOS from `namei_msdos.o`.
- Builds `fat_test.o` when `CONFIG_FAT_KUNIT_TEST` is enabled.

Important interactions:
- Mirrors the Kconfig split between shared FAT infrastructure, VFAT long-name support, MSDOS name lookup, and KUnit tests.
