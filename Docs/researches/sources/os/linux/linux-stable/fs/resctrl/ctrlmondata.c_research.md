# File Research: sources/os/linux/linux-stable/fs/resctrl/ctrlmondata.c

Implements resctrl user-facing data file handlers for control schemata, monitoring reads, MBA MBps event selection, and `io_alloc` controls.

Key responsibilities:
- Parses `schemata` writes by resource/domain pairs, validating MBA bandwidth values and cache CBMs against hardware limits, minimum CBM bits, sparse-mask support, exclusive groups, and pseudo-locked regions.
- Stages control updates in per-domain `staged_config`, then commits through `resctrl_arch_update_domains()`.
- Handles pseudo-lock setup by accepting one valid cache CBM, binding it to `rdtgrp->plr`, and invoking `rdtgroup_pseudo_lock_create()`.
- Shows schemata and allocation sizes for normal groups and special pseudo-lock states.
- Reads monitor event data via `mon_event_read()`, choosing domain-local CPUs or any-CPU reads, allocating architecture monitor context when needed, and printing `Error`, `Unavailable`, `Unassigned`, integer, or fixed-point values.
- Implements `mba_MBps_event` selection between `mbm_local_bytes` and `mbm_total_bytes`.
- Implements `io_alloc`, reserving the highest CLOSID for I/O cache allocation, initializing its CBM, syncing CDP peer CBMs, and parsing per-domain or global `*=` CBM writes.

Important dependencies:
- Uses `rdtgroup_mutex` through `rdtgroup_kn_lock_live()` and CPU hotplug exclusion through `cpus_read_lock()`.
- Calls into `rdtgroup.c` for CLOSID allocation, overlap checks, pseudo-lock helpers, and schema lists.
- Calls architecture hooks for reading counters and updating control domains.

Notable invariants:
- User writes require trailing newline.
- Duplicate domain entries are rejected.
- MBA software-controller writes update `mbps_val[]` rather than hardware control MSRs directly.
- `io_alloc` consumes a fixed highest CLOSID and refuses enablement if that CLOSID is already used by a group.
