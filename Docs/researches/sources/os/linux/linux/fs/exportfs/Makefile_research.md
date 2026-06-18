# File Research: sources/os/linux/linux/fs/exportfs/Makefile

Read status: complete, 7 lines.

This Makefile builds the generic filesystem export support module.

Key responsibilities:
- Adds `exportfs.o` when `CONFIG_EXPORTFS` is enabled.
- Defines `exportfs-objs := expfs.o`, so the module/object is composed from `expfs.c`.

Research notes:
- The build surface is intentionally minimal.
- The functional implementation for this directory is in `fs/exportfs/expfs.c`.
