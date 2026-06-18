# File Research: sources/os/linux/linux/fs/afs/Makefile

Purpose: lists object files linked into the `kafs` module/built-in object.

Key interfaces:
- `obj-$(CONFIG_AFS_FS) := kafs.o`.
- `kafs-y` includes address management, callbacks, cells, cache-manager service, directory logic, dynroot, file I/O, flocking, fs/vl/yfs clients, inode/super, rotation/probing, security, server/volume management, write, xattr.
- `kafs-$(CONFIG_PROC_FS) += proc.o`.

Implementation notes:
- The files in this work item are part of the core `kafs-y` object set.
- Procfs support is conditional, but address preferences and cell code include proc-facing hooks when proc is available through other compilation units.
