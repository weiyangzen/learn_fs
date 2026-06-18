# File Research: sources/os/linux/linux/fs/resctrl/monitor.c

## Purpose
Implements resctrl monitoring internals: RMID allocation and limbo recycling, CQM/LLC occupancy cleanup, MBM bandwidth accounting, MBA software-controller feedback, configurable MBM event filters, assignable MBM counters, and monitoring resource initialization/teardown.

## Main Responsibilities
- Maintain global RMID free/limbo state.
- Track dirty RMIDs until LLC occupancy falls below the reallocation threshold.
- Read L3 and package monitoring events and aggregate child monitor groups.
- Periodically refresh MBM counters and compute MBps.
- Adjust MBA throttling in software-controller mode.
- Manage assignable MBM hardware counters and event transaction filters.
- Initialize monitor event metadata and per-domain state.

## Key Types and State
- `struct rmid_entry`: tracks one CLOSID/RMID pair or RMID index, busy-domain count, and free-list membership.
- `rmid_free_lru`: LRU list of clean/free RMIDs.
- `closid_num_dirty_rmid`: per-CLOSID dirty RMID count for architectures where RMID depends on CLOSID.
- `rmid_limbo_count`: count of unused but dirty RMIDs.
- `rmid_ptrs`: indexed RMID entry table.
- `resctrl_rmid_realloc_threshold`: occupancy threshold below which RMID can be reused.
- `resctrl_rmid_realloc_limit`: maximum allowed threshold.
- `mon_event_all[]`: global table of supported monitor events, enabled/configured by architecture code.

## Important Control Flow
- RMID allocation:
  - `setup_rmid_lru_list()` allocates `rmid_ptrs`, initializes all entries as free, and reserves the default RMID.
  - `alloc_rmid()` gets a compatible free entry for a CLOSID.
  - `free_rmid()` either adds the entry to limbo if LLC occupancy monitoring is enabled or returns it directly to free LRU.
- Limbo recycling:
  - `add_rmid_to_limbo()` marks the RMID busy in every L3 monitor domain and schedules `cqm_limbo`.
  - `__check_limbo()` reads LLC occupancy for busy RMIDs and releases clean entries.
  - `cqm_handle_limbo()` repeats scans until no busy RMIDs remain.
- Counter reads:
  - `__l3_mon_event_count()` reads one L3 domain or resets counters on first initialization.
  - `__l3_mon_event_count_sum()` sums SNC domains sharing one L3 cache id.
  - `__mon_event_count()` dispatches by resource id.
  - `mon_event_count()` also adds child monitor-group counts for control groups.
- MBM/MBA:
  - `mbm_update_one_event()` reads MBM events and updates bandwidth state.
  - `mbm_handle_overflow()` periodically updates all groups and optionally calls `update_mba_bw()`.
  - `update_mba_bw()` compares measured bandwidth against user target and adjusts MBA MSR values by hardware granularity.
- Assignable counters:
  - `mbm_cntr_get/alloc/free()` manage per-domain counter slots.
  - `rdtgroup_assign_cntrs()` assigns default MBM counters for new groups when enabled.
  - `rdtgroup_unassign_cntrs()` releases counters on group deletion.
  - `mbm_L3_assignments_show/write()` exposes per-event/per-domain assignment state.
- Event filters:
  - `event_filter_show/write()` displays and updates memory transaction masks for configurable MBM events.
  - Changes are propagated to existing assigned counters through `resctrl_update_cntr_allrdtgrp()`.

## Dependencies and Integration
- Includes `monitor_trace.h` and defines tracepoints for RMID limbo occupancy reads.
- Called by `rdtgroup.c` for mount init, domain hotplug, group creation/deletion, and info-file handlers.
- Called by `ctrlmondata.c` indirectly through `mon_event_read()` and `mon_event_count()`.
- Relies on architecture hooks for RMID indexing, monitor context allocation, RMID/counter reads, counter resets, and counter configuration.

## Concurrency and Locking
- RMID, counter assignment, and group traversal require `rdtgroup_mutex`.
- Domain list traversal also requires CPU hotplug protection where noted.
- Delayed workers take `cpus_read_lock()` and `rdtgroup_mutex`.
- Work scheduling avoids nohz_full CPUs where possible via `cpumask_any_housekeeping()`.

## Error Handling
- RMID allocation distinguishes `-EBUSY` dirty-RMID pressure from `-ENOSPC` exhaustion.
- Monitor context allocation failures are rate-limited warnings.
- Assignable counter read without assignment uses `-ENOENT`, later rendered as `Unassigned`.
- Event filter parsing reports invalid transaction names through `last_cmd_status`.

## Research Notes
This file is the resource-accounting core of resctrl monitoring. The important invariants are RMID lifecycle correctness, matching CLOSID/RMID indexing across architectures, delayed-work cancellation on hotplug/unmount, and consistency between assignable counter mode and legacy BMEC configuration files.
