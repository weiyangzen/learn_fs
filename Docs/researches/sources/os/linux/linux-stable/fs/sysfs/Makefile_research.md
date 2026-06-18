# File Research: sources/os/linux/linux-stable/fs/sysfs/Makefile

Purpose: Builds the sysfs virtual filesystem implementation.

Key responsibilities:
- Adds `file.o`, `dir.o`, `symlink.o`, `mount.o`, and `group.o` to `obj-y`.

Important interactions:
- Sysfs is built as core kernel code when enabled, with functionality split across file attributes, directories, symlinks, mounting, and attribute groups.

Notable invariants and risks:
- There is no conditional object split inside this Makefile; `CONFIG_SYSFS` controls entry from the parent build.
