# File Research: sources/os/linux/linux/fs/resctrl/Kconfig

Kconfig options for the CPU resource control filesystem.

Defines:
- `RESCTRL_FS`
  - User-visible boolean: “CPU Resource Control Filesystem (resctrl)”.
  - Depends on `ARCH_HAS_CPU_RESCTRL`.
  - Selects `KERNFS`.
  - Selects `PROC_CPU_RESCTRL` when `PROC_FS` is enabled.
  - Provides a mountable `resctrl` filesystem for grouping tasks and controlling/monitoring memory-system resources such as cache and memory bandwidth.
- `RESCTRL_FS_PSEUDO_LOCK`
  - Internal boolean depending on `RESCTRL_FS`.
  - Enables software pseudo-locking to pin data in a cache portion.
- `RESCTRL_RMID_DEPENDS_ON_CLOSID`
  - Internal boolean depending on `RESCTRL_FS`.
  - Used when RMID allocation depends on CLOSID, causing CLOSID allocation to search for a clean RMID.

Research notes:
- This file is configuration only; implementation objects are selected in the sibling Makefile.
