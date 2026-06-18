# File Research: sources/os/linux/linux-stable/fs/resctrl/internal.h

Shared private header for the resctrl filesystem implementation.

Key definitions:
- `struct rdt_fs_context`: mount option state for CDP, MBA software controller, and debug mode.
- `struct mon_evt`, `struct mon_data`, and `struct rmid_read`: monitor event metadata, kernfs private event-file metadata, and cross-CPU monitor-read request state.
- `enum rdt_group_type` and `enum rdtgrp_mode`: distinguish control/monitor groups and shareable, exclusive, pseudo-lock setup, and pseudo-locked modes.
- `struct mongroup` and `struct rdtgroup`: core in-memory group state, including kernfs node, CLOSID, RMID, CPU mask, children, mode, MBA event, and pseudo-lock region.
- `struct rftype`: descriptor for each resctrl kernfs file, including visibility flags and callbacks.
- `struct mbm_state`: cached MBM bandwidth calculation state.

Shared APIs:
- Declares schemata, monitor, CLOSID/RMID, pseudo-lock, file visibility, MBM assignment, BMEC, and `io_alloc` functions used across `rdtgroup.c`, `ctrlmondata.c`, `monitor.c`, and `pseudo_lock.c`.
- Provides pseudo-lock stub implementations when `CONFIG_RESCTRL_FS_PSEUDO_LOCK` is disabled.
- Provides `cpumask_any_housekeeping()` to prefer non-`nohz_full` CPUs for monitor work/IPIs.

Notable invariants:
- Most helpers assume `rdtgroup_mutex` is held.
- Domain walks commonly require CPU hotplug protection.
- `MAX_BINARY_BITS` bounds fixed-point monitor event formatting.
