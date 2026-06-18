# File Research: sources/os/linux/linux-stable/fs/resctrl/monitor.c

Implements resctrl monitoring state, RMID allocation/reclaim, MBM bandwidth accounting, overflow/limbo workers, monitor event registration, and assignable MBM counter policy.

Key responsibilities:
- Maintains RMID free LRU and limbo state using `struct rmid_entry`; supports architectures where RMID identity depends on CLOSID.
- Reclaims limbo RMIDs by reading LLC occupancy and freeing entries once occupancy drops below `resctrl_rmid_realloc_threshold`.
- Allocates RMIDs, frees them into limbo when occupancy monitoring is enabled, and exposes cleanest-CLOSID selection for MPAM-like architectures.
- Reads L3 occupancy/MBM and PERF_PKG events; sums child monitor groups into parent control groups.
- Keeps per-RMID MBM state and computes MBps deltas once per overflow interval.
- Runs MBA software-controller feedback by comparing measured MBM bandwidth with user MBps targets and adjusting MBA throttle values.
- Registers available monitor events in `mon_event_all[]`, with architecture enablement through `resctrl_enable_mon_event()`.
- Implements BMEC/event-filter display and writes for assignable MBM events.
- Implements `mbm_assign_mode`, `mbm_assign_on_mkdir`, counter availability, and per-group `mbm_L3_assignments`.

Important workflows:
- `setup_rmid_lru_list()` allocates global RMID entries on mount and reserves the default RMID.
- `cqm_handle_limbo()` periodically scans busy RMIDs for one domain and reschedules while busy entries remain.
- `mbm_handle_overflow()` periodically updates MBM counters for all groups and child monitor groups, then optionally updates MBA software control.
- Assignable counter mode clears software RMID state and hardware counter assignment state when toggled.

Notable invariants:
- RMID and counter assignment lists are protected by `rdtgroup_mutex`.
- Overflow and limbo work prefers housekeeping CPUs and migrates away from `nohz_full` CPUs.
- In MBM counter-assignment mode, unassigned counters are reported to userspace as `Unassigned`.
