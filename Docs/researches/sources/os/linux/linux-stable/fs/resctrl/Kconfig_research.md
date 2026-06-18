# File Research: sources/os/linux/linux-stable/fs/resctrl/Kconfig

## Purpose
Defines Kconfig options for the CPU Resource Control filesystem, `resctrl`.

## Options
- `RESCTRL_FS`: mountable resource-control filesystem, depends on `ARCH_HAS_CPU_RESCTRL`, selects `KERNFS`, and selects `PROC_CPU_RESCTRL` when procfs is enabled.
- `RESCTRL_FS_PSEUDO_LOCK`: internal option for cache pseudo-locking support, depends on `RESCTRL_FS`.
- `RESCTRL_RMID_DEPENDS_ON_CLOSID`: architecture-selected option for systems where RMID allocation depends on CLOSID.

## User-Visible Behavior
When enabled, userspace can mount `resctrl` to group tasks and manage hardware cache/memory bandwidth monitoring and control resources. If unused, controls remain quiescent and permissive.
