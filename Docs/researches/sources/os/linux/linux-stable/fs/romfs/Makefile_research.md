# File Research: sources/os/linux/linux-stable/fs/romfs/Makefile

Build glue for the ROMFS filesystem.

Key behavior:
- Builds `romfs.o` when `CONFIG_ROMFS_FS` is enabled.
- Always includes `storage.o` and `super.o`.
- On NOMMU builds, includes `mmap-nommu.o` only when `CONFIG_ROMFS_ON_MTD` is enabled.

Purpose:
- Keeps direct MTD mmap support limited to NOMMU MTD-backed configurations.
