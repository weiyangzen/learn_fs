# File Research: sources/os/linux/linux/fs/resctrl/internal.h

## Purpose
Private header for the Linux resctrl filesystem implementation. It defines shared in-kernel data structures, flags, helper prototypes, and pseudo-locking stubs used across `rdtgroup.c`, `ctrlmondata.c`, `monitor.c`, and `pseudo_lock.c`.

## Main Responsibilities
- Define resctrl filesystem context and kernfs-facing file descriptors.
- Define monitoring event metadata and per-file monitor private data.
- Define rdtgroup, mongroup, and RMID read state.
- Centralize rftype flags used to decide which files appear in which resctrl directories.
- Declare cross-file functions for schemata, monitor reads, MBA assignment controls, I/O allocation, CLOSID/RMID allocation, pseudo-locking, and file visibility.

## Key Types
- `struct rdt_fs_context`: mount option state for CDP, MBA MBps, and debug mode.
- `struct mon_evt`: monitor event descriptor, including event id, resource id, name, configuration mask, fixed-point formatting metadata, enable state, and architecture private data.
- `struct mon_data`: `kernfs_node->priv` payload for monitor event files; identifies resource, domain/cache id, event, and whether the file is a sum file.
- `struct rmid_read`: read request/result passed to `mon_event_count()` across local or remote CPU calls.
- `enum rdt_group_type`: distinguishes control groups from monitor-only groups.
- `enum rdtgrp_mode`: shareable, exclusive, pseudo-lock setup, and pseudo-locked group modes.
- `struct mongroup`: monitor-group state, parent relationship, child list, and RMID.
- `struct rdtgroup`: core resctrl group object with kernfs node, CLOSID, CPU mask, lifecycle flags, type, monitor state, mode, MBA event selection, and pseudo-lock region pointer.
- `struct rftype`: describes resctrl files, permissions, kernfs operations, visibility flags, show callback, and write callback.
- `struct mbm_state`: cached previous MBM bytes and computed bandwidth.

## Important Constants and Flags
- `CQM_LIMBOCHECK_INTERVAL`: RMID limbo scan period.
- `MAX_BINARY_BITS`: limit for fixed-point monitor-event fractional bits.
- `RDT_DELETED`: rdtgroup lifecycle flag used with `waitcount`.
- `RFTYPE_*`: visibility flags for top/info/base/control/monitor/cache/MB/debug/assignment/perf-package files.
- `RFTYPE_FLAGS_CPUS_LIST`: marks `cpus_list` formatting/parsing.

## Inline Helpers
- `cpumask_any_housekeeping()`: chooses a CPU from a mask, preferring non-`nohz_full` housekeeping CPUs and optionally excluding one CPU.
- `rdt_fc2context()`: converts `fs_context` to resctrl context.
- `rdt_kn_name()`: safely reads a kernfs node name under `rdtgroup_mutex`.

## Dependencies and Integration
- Includes `<linux/resctrl.h>`, kernfs, fs context, and tick/nohz support.
- Exposes `resctrl_schema_all`, `rdt_all_groups`, `rdtgroup_default`, `rdtgroup_mutex`, `max_name_width`, and `debugfs_resctrl`.
- Provides stubs for pseudo-locking when `CONFIG_RESCTRL_FS_PSEUDO_LOCK` is disabled, allowing the rest of resctrl to compile without feature guards at every call site.

## Research Notes
This header is the internal contract for the resctrl filesystem. Most correctness constraints in the implementation depend on these structures being consistently interpreted across allocation control, monitor accounting, mount lifecycle, and pseudo-locking.
