# File Research: sources/os/linux/linux/mm/vmstat.c

## Purpose

`vmstat.c` implements Linux VM statistics collection, folding, export, and diagnostic reporting. It owns global zone, node, NUMA, and VM event counter storage, provides fast per-CPU update paths, periodically folds per-CPU deltas into global counters, and exposes the counters through `/proc`, sysctls, and debugfs fragmentation reports.

The file is performance-sensitive because many memory-management paths update these counters in allocation, reclaim, migration, compaction, and swap flows. It trades exactness for low contention by accumulating small per-CPU signed deltas and folding them only when thresholds are exceeded or background workers run.

## Main Data And State

- `vm_zone_stat[]`, `vm_node_stat[]`, and `vm_numa_event[]` are global atomic counter arrays.
- `vm_event_states` is a per-CPU event counter array when `CONFIG_VM_EVENT_COUNTERS` is enabled.
- Per-zone `per_cpu_zonestats` and per-node `per_cpu_nodestats` hold local counter deltas and thresholds.
- NUMA statistics can be enabled or disabled with `vm.numa_stat`; disabling clears zone and global NUMA counters.
- `nr_memmap_boot_pages` and `nr_memmap_pages` count pages consumed by `struct page` and page extension metadata.
- Under SMP, per-CPU delayed work and the `shepherd` work item keep vmstat deltas folded without waking isolated CPUs unnecessarily.

## Counter Update Paths

The file exports zone and node counter modification APIs used across the mm subsystem:

- `__mod_zone_page_state()`, `__inc_zone_state()`, `__dec_zone_state()`
- `__mod_node_page_state()`, `__inc_node_state()`, `__dec_node_state()`
- `mod_zone_page_state()`, `inc_zone_page_state()`, `dec_zone_page_state()`
- `mod_node_page_state()`, `inc_node_page_state()`, `dec_node_page_state()`

On systems with `CONFIG_HAVE_CMPXCHG_LOCAL`, updates use `this_cpu_try_cmpxchg()` to avoid disabling interrupts. Other systems serialize with `local_irq_save()`. On PREEMPT_RT, the internal update path uses `preempt_disable_nested()` so per-CPU RMW sequences remain safe even when local locks do not fully disable preemption.

Node counters that are logically byte counters are stored as page counts in the compact per-CPU delta arrays, with validation that global updates arrive in page-sized multiples.

## Folding And Thresholds

`calculate_normal_threshold()` scales per-CPU batching thresholds by online CPU count and zone size, capped at 125. `calculate_pressure_threshold()` lowers thresholds when watermark drift could hide pressure. `refresh_zone_stat_thresholds()` installs thresholds and computes `percpu_drift_mark` where drift can threaten low/min watermarks.

`refresh_cpu_vm_stats()` drains current CPU zone and node diffs, updates per-zone and per-node atomics, accumulates global deltas, and optionally decays or drains per-CPU pagesets. On NUMA systems, remote per-CPU pagesets can expire and drain to reduce remote free-page hoarding. `cpu_vm_stats_fold()` handles CPU-offline folding.

`quiet_vmstat()` is the NOHZ-facing path: if a CPU is going idle and has pending deltas, it refreshes counters without canceling outstanding delayed work. `vmstat_shepherd()` periodically scans online CPUs with disabled or idle workers and queues needed flushes, skipping isolated CPUs to avoid disturbance.

## Reporting Interfaces

The file defines `vmstat_text[]`, the exported text names for zone, NUMA, node, global VM, and VM event counters. It includes counters for workingset, reclaim, compaction, huge pages, zswap, zsmalloc, NUMA balancing, swap, ballooning, KSM, TLB flushes, stack usage, and architecture-specific direct-map events based on Kconfig.

`/proc/vmstat` is implemented by `vmstat_op`: `vmstat_start()` snapshots global counters, folds NUMA events, computes dirty limits, adds memmap counters, and folds per-CPU VM events. `vmstat_show()` prints name/value pairs and appends deprecated `nr_unstable 0` for userspace compatibility.

Other proc entries:

- `/proc/buddyinfo` prints free block counts by order.
- `/proc/pagetypeinfo` prints free pages and pageblocks by migrate type, and page-owner mixed block counts when available.
- `/proc/zoneinfo` prints node, zone, watermarks, reserves, per-zone stats, NUMA event stats, pagesets, and highatomic information.

Sysctls:

- `vm.stat_interval` controls vmstat delayed-work cadence.
- `vm.stat_refresh` forces per-CPU stat refresh and warns on unexpected negative counters.
- `vm.numa_stat` toggles NUMA accounting and clears counters when disabled.

Debugfs compaction entries under `extfrag/` expose unusable-free-space and external-fragmentation indexes.

## Fragmentation Helpers

With `CONFIG_COMPACTION`, `fill_contig_page_info()`, `fragmentation_index()`, and `extfrag_for_order()` derive diagnostic views of free memory layout by walking each zone's free areas. These are not migration predictors; they intentionally avoid expensive estimates of movable-page compaction potential.

## Integration Points

This file is central infrastructure for allocator, reclaim, compaction, zsmalloc, zswap, workingset, memcg, NUMA balancing, and procfs/debugfs observability. `init_mm_internals()` creates `mm_percpu_wq`, registers CPU hotplug callbacks, starts the shepherd timer, creates proc entries, and registers the sysctl table. `init_mm_internals()` is therefore a key mm bootstrap hook.

## Concurrency And Invariants

- Fast counter updates must preserve per-CPU atomicity while minimizing IRQ/preemption cost.
- Global counters are approximate and can transiently lag or be clamped for readers.
- Zone and node stat thresholds bound drift; pressure thresholds are tightened near watermarks.
- `vmstat_refresh()` deliberately warns on negative counters except for known transiently negative stats.
- Proc/debugfs walkers hold zone locks where needed, but some diagnostic reads use `data_race()` because the values are informational.
- CPU hotplug folding must run after worker disable and before offline CPU state disappears.

## Risks And Test Focus

Important risks are off-by-one enum/text table mismatches, counter drift hiding watermarks, negative counter regressions, isolated-CPU interference, and locking mistakes in diagnostic walkers. Validation should cover `/proc/vmstat` name count consistency, CPU hotplug folding, NUMA stat toggling, `stat_refresh` warnings, high CPU count threshold behavior, and fragmentation output under compaction-enabled builds.
