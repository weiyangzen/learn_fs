# File Research: sources/os/linux/linux/fs/resctrl/ctrlmondata.c

## Purpose
Implements user-facing resctrl file handlers for control and monitor data: `schemata`, `mon_data/*` event files, `mba_MBps_event`, and `io_alloc`/`io_alloc_cbm`. It validates text written through kernfs, stages allocation changes, commits them through architecture hooks, and formats monitoring/control values back to userspace.

## Main Responsibilities
- Parse CAT/CDP cache bitmasks and MBA bandwidth values from `schemata`.
- Enforce sharing, exclusivity, and pseudo-locking overlap rules before committing CBMs.
- Display current schemata and pseudo-lock state.
- Read monitoring counters through `mon_event_read()` and print normal, unavailable, unassigned, error, or fixed-point values.
- Support MBA software-controller event selection.
- Support `io_alloc`, which reserves the highest CLOSID for I/O allocation and lets users configure its CBM.

## Key Types
- `struct rdt_parse_data`: carries `closid`, group mode, and current value text into parsers.
- `ctrlval_parser_t`: parser callback type used by `parse_line()`.
- `decplaces[]`: fixed-point decimal precision table for monitor events with binary fractional bits.

## Important Control Flow
- `rdtgroup_schemata_write()`:
  - Requires newline-terminated input.
  - Locks a live rdtgroup using `rdtgroup_kn_lock_live()`.
  - Rejects writes to already pseudo-locked groups.
  - Clears all staged configs, parses each `<resource>:<domain=value;...>` line, then calls `resctrl_arch_update_domains()` for non-MBA-SC resources.
  - If group is in `RDT_MODE_PSEUDO_LOCKSETUP`, calls `rdtgroup_pseudo_lock_create()` after staging one cache region.
- `parse_cbm()`:
  - Rejects duplicate domains, pseudo-lock hierarchy conflicts, invalid masks, overlap with pseudo-locked regions, overlap with exclusive groups, and illegal overlap for exclusive/pseudo-locksetup modes.
  - Stages the new CBM in `d->staged_config[s->conf_type]`.
- `parse_bw()`:
  - Validates MBA values with hardware limits/granularity unless MBA software controller is enabled.
  - In MBA-SC mode stores MBps target in `d->mbps_val[closid]` instead of staging MSR control values.
- `rdtgroup_mondata_show()`:
  - Resolves `struct mon_data` from `kn->priv`.
  - Handles normal domain reads and L3 SNC sum files.
  - Prints `Error`, `Unavailable`, `Unassigned`, integer values, or fixed-point values.
- `resctrl_io_alloc_write()`:
  - Parses a boolean enable value.
  - Reserves/frees the highest usable CLOSID.
  - Initializes CBMs for the reserved CLOSID and enables/disables architecture I/O allocation.
- `resctrl_io_alloc_cbm_write()`:
  - Parses `domain=mask` entries plus global `*=mask`.
  - Keeps CDP code/data peer CBMs synchronized for the I/O CLOSID.

## Dependencies and Integration
- Depends on `internal.h` for rdtgroup types, global schema list, last-command status helpers, monitor structures, and pseudo-locking declarations.
- Calls architecture hooks including `resctrl_arch_update_domains()`, `resctrl_arch_get_config()`, `resctrl_arch_io_alloc_enable()`, `resctrl_arch_mon_ctx_alloc/free()`, and monitor read hooks indirectly through `mon_event_count()`.
- Shares staged-domain workflow with `rdtgroup.c`.
- Integrates with `monitor.c` through `mon_event_count()` and MBM counter assignment state.

## Concurrency and Locking
- File writes and reads use `rdtgroup_kn_lock_live()` or explicit `cpus_read_lock()` plus `rdtgroup_mutex`.
- Domain-list walks assert CPU hotplug protection with `lockdep_assert_cpus_held()`.
- Monitor reads pick housekeeping CPUs where possible and use `smp_call_on_cpu()` or `smp_call_function_any()` depending on nohz/full and event constraints.

## Error Handling
- Writes consistently update `last_cmd_status` through `rdt_last_cmd_*()` before returning `-EINVAL`, `-ENOENT`, `-ENODEV`, or `-ENOSPC`.
- Monitoring counter read errors are intentionally translated to user-visible strings in event files.
- Staged configs are cleared on every exit path from schemata and I/O CBM writes.

## Research Notes
This file is the primary parser/formatter boundary for resctrl allocation control. The highest-risk behaviors are textual grammar compatibility, staged-config cleanup, pseudo-lock overlap checks, and interactions between MBA-SC, assignable MBM counters, and `io_alloc` CLOSID reservation.
