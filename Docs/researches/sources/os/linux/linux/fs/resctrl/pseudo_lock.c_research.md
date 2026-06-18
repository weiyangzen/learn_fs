# File Research: sources/os/linux/linux/fs/resctrl/pseudo_lock.c

## Purpose
Implements resctrl cache pseudo-locking support. A resctrl group can be placed into pseudo-lock setup mode, configured with a CAT CBM, locked into cache by an architecture-specific thread, and exposed to userspace through a character device and debugfs measurement hook.

## Main Responsibilities
- Allocate and initialize pseudo-lock regions.
- Restrict group files while pseudo-lock setup is in progress.
- Validate that pseudo-locking is allowed for the group and platform.
- Prevent overlapping pseudo-locked regions in a cache hierarchy.
- Constrain CPU low-power states while a region is locked.
- Create/destroy pseudo-lock character devices.
- Provide NOMMU-style `mmap_prepare` mapping of the locked kernel buffer.
- Provide debugfs-triggered latency/residency measurements.

## Key State
- `pseudo_lock_major`: shared char-device major number.
- `pseudo_lock_minor_avail`: bitmap of available pseudo-lock minors.
- `pseudo_lock_class`: device class named `pseudo_lock`, with devnodes under `pseudo_lock/<group>`.
- `struct pseudo_lock_pm_req`: PM QoS request list entry used to constrain C-states for CPUs in the cache domain.

## Important Control Flow
- Setup entry:
  - `rdtgroup_locksetup_enter()` rejects default group, CDP-enabled systems, unsupported prefetch-disable platforms, existing monitoring, assigned tasks, or assigned CPUs.
  - Restricts `tasks`, `cpus`, `cpus_list`, and optionally `mon_groups`.
  - Allocates `rdtgrp->plr` and frees the group RMID because pseudo-lock groups cannot monitor.
- Setup exit:
  - `rdtgroup_locksetup_exit()` allocates a new RMID if monitoring is supported, restores file permissions, and frees the pseudo-lock region.
- Region creation:
  - `rdtgroup_pseudo_lock_create()` initializes region size/line size/CPU, allocates contiguous kernel memory, adds PM QoS constraints, runs `resctrl_arch_pseudo_lock_fn()` on the target CPU, allocates a minor, creates debugfs and device nodes, switches mode to `RDT_MODE_PSEUDO_LOCKED`, and frees the CLOSID.
- Region removal:
  - `rdtgroup_pseudo_lock_remove()` handles both setup and locked states, removing QoS constraints, debugfs, char device, minor allocation, CLOSID, and region memory.
- Mapping:
  - `pseudo_lock_dev_open()` finds a region by minor and increments rdtgroup waitcount.
  - `pseudo_lock_dev_mmap_prepare()` requires the caller affinity to be a subset of the cache-domain CPUs, requires shared mapping, validates offsets/lengths, zeroes the mapped bytes, and remaps the physical backing buffer.
- Measurements:
  - `pseudo_lock_measure_trigger()` accepts selector `1`, `2`, or `3`.
  - `pseudo_lock_measure_cycles()` runs architecture latency/L2/L3 residency measurement functions on a CPU in the locked domain.

## Dependencies and Integration
- Called from `rdtgroup.c` mode transitions, removal paths, and resctrl init/exit.
- Called from `ctrlmondata.c` schemata parsing/commit path when group mode is `RDT_MODE_PSEUDO_LOCKSETUP`.
- Uses architecture hooks for pseudo-lock execution, prefetch-disable detection, and measurements.
- Uses cacheinfo to derive cache line size and region size.

## Concurrency and Locking
- Uses `rdtgroup_mutex` for group lookup, state changes, and char-device open/release.
- Temporarily releases `rdtgroup_mutex` around debugfs/device creation to avoid lock ordering problems with mmap and filesystem locks.
- Uses `waitcount` and `RDT_DELETED` to keep rdtgroups alive while devices or kernfs operations hold references.

## Error Handling
- Writes descriptive `last_cmd_status` messages for unsupported platform state, allocation failure, invalid group state, device creation failure, and interrupted locking thread.
- Creation failure unwinds in reverse order: device/debugfs/minor, PM QoS, region data.
- If CPU/domain disappears, user-visible operations return `-ENODEV`.

## Research Notes
Pseudo-locking has strong cross-file coupling: `rdtgroup.c` controls mode and group lifetime, `ctrlmondata.c` supplies the validated CBM, and this file owns the locking/mapping/device mechanics. The main risks are teardown races, CPU hotplug, permission restoration, and deadlock avoidance around device/debugfs creation.
