# File Research: sources/os/linux/linux-stable/fs/affs/Kconfig
- Purpose: Defines configuration for Amiga Fast File System support.
- Main option: `AFFS_FS` enables AFFS filesystem support.
- User-facing role: Supports mounting Amiga FFS/OFS variants and related disk-file use cases.
- Integration: Controls build of `fs/affs/` through the top-level filesystem Kconfig and Makefile.
- Research notes: Feature variants are largely runtime mount/format choices rather than separate Kconfig switches.
