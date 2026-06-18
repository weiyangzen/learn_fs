# File Research: sources/os/linux/linux-stable/fs/resctrl/Makefile

## Purpose
Build rules for resctrl filesystem objects.

## Behavior
- Builds `rdtgroup.o`, `ctrlmondata.o`, and `monitor.o` when `CONFIG_RESCTRL_FS=y`.
- Builds `pseudo_lock.o` when `CONFIG_RESCTRL_FS_PSEUDO_LOCK=y`.
- Adds `-I$(src)` to `monitor.o` compile flags to support recursive `define_trace.h` include behavior.

## Role
Connects resctrl Kconfig selections to the filesystem implementation object files.
