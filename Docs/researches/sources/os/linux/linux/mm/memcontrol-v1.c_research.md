# File Research: sources/os/linux/linux/mm/memcontrol-v1.c

## Purpose

Implements legacy cgroup v1 memory controller behavior that is no longer shared with the cgroup v2 memory controller. This includes soft limits, memory+swap accounting compatibility, threshold and OOM eventfd notifications, legacy cgroup files, force-empty support, per-memcg swappiness, kmem/tcp counters, and v1 statistics formatting.

## Major State

The file defines v1-specific state around:

- `soft_limit_tree`: per-NUMA-node RB-trees of cgroups exceeding soft limits.
- `memcg_oom_lock`: global spinlock for v1 OOM notification and OOM lock state.
- `memcg_oom_waitq`: waitqueue for userspace OOM handling.
- `memcg_max_mutex`: serializes updates to memory and memsw limits.
- `memcg1_events_percpu`: per-CPU page event counters and rate-limit targets.
- eventfd registration objects for cgroup v1 `cgroup.event_control`.

## Soft Limit Reclaim

Soft-limit tracking is built around `struct mem_cgroup_tree_per_node`, which stores an RB-tree and cached rightmost node for the largest soft-limit excess on each NUMA node.

Key functions:

- `soft_limit_excess()`: computes `memory.current - soft_limit`.
- `__mem_cgroup_insert_exceeded()`: inserts a per-node memcg entry by excess.
- `__mem_cgroup_remove_exceeded()`: removes an entry.
- `memcg1_update_tree()`: updates the soft-limit tree for a memcg and its ancestors.
- `memcg1_remove_from_trees()`: removes all per-node entries for a memcg.
- `memcg1_soft_limit_reclaim()`: selects over-limit cgroups and reclaims from them.

If multigenerational LRU is enabled, soft-limit tree reclaim is bypassed and `lru_gen_soft_reclaim()` is used from `memcg1_update_tree()`.

Soft-limit reclaim is best effort. It skips higher-order allocations, caps loops with `MEM_CGROUP_MAX_RECLAIM_LOOPS` and `MEM_CGROUP_MAX_SOFT_LIMIT_RECLAIM_LOOPS`, and tolerates races in tree state.

## Charge and Uncharge Events

`memcg1_commit_charge()` updates v1 event accounting on folio charge:

- counts `PGPGIN`;
- increments per-CPU page event counters;
- checks threshold and soft-limit events.

`memcg1_uncharge_batch()` does the corresponding batched page-out accounting and event checks.

Rate limiting is page-event based:

- threshold checks every `THRESHOLDS_EVENTS_TARGET` pages;
- soft-limit checks every `SOFTLIMIT_EVENTS_TARGET` pages.

On `CONFIG_PREEMPT_RT`, event checks are skipped for this v1 path.

## Swap and memsw Accounting

`do_memsw_account()` is true only on legacy hierarchy. This file provides v1-specific memory+swap lifetime handling:

- `memcg1_swapout()` transfers a folio's memsw charge to a swap entry, records the swap cgroup id, clears folio memcg data, adjusts memory/memsw counters, and updates page-out events.
- `memcg1_swapin()` removes duplicate swap-slot charge after a charged page enters swapcache.

The swapout path handles offlined memcgs by charging the closest online ancestor via `mem_cgroup_private_id_get_online()`.

## Threshold Notifications

Threshold notification support backs legacy eventfd monitoring of usage files.

Important functions:

- `mem_cgroup_usage()`: reads memory or memory+swap usage.
- `__mem_cgroup_threshold()`: detects crossed thresholds and signals eventfds.
- `mem_cgroup_threshold()`: applies threshold checks up the hierarchy.
- `__mem_cgroup_usage_register_event()`: parses threshold arguments, allocates and sorts threshold arrays, and publishes them through RCU.
- `__mem_cgroup_usage_unregister_event()`: rebuilds threshold arrays after eventfd removal.

Threshold arrays maintain a `current_threshold` index to avoid scanning the whole array unless usage crosses a boundary. Updates are protected by `thresholds_lock` and readers use RCU.

## cgroup.event_control Compatibility

The file implements the deprecated cgroup v1 `cgroup.event_control` ABI.

`memcg_write_event_control()` parses:

`<event_fd> <control_fd> <args>`

It resolves supported control files by name:

- `memory.usage_in_bytes`
- `memory.memsw.usage_in_bytes`
- `memory.oom_control`
- `memory.pressure_level`

It then installs callbacks in `struct mem_cgroup_event`, attaches to the eventfd poll waitqueue, and links the event into `memcg->event_list`.

Cleanup flow:

- `memcg_event_wake()` detects `EPOLLHUP`.
- `memcg_event_remove()` unregisters and frees from workqueue context.
- `memcg1_css_offline()` schedules removal of all remaining events on cgroup offline.

The comments explicitly mark this mechanism as deprecated and not for new files.

## OOM Handling

Legacy v1 supports OOM notifications and optional userspace OOM handling.

Key functions:

- `mem_cgroup_oom_notify()`: signals registered OOM eventfds for a subtree.
- `mem_cgroup_oom_trylock()`: marks a memcg subtree as OOM-locked.
- `mem_cgroup_oom_unlock()`: clears OOM locks.
- `mem_cgroup_mark_under_oom()` and `mem_cgroup_unmark_under_oom()`: maintain subtree `under_oom` counters.
- `memcg1_oom_prepare()`: prepares charge-path OOM handling.
- `memcg1_oom_finish()`: releases OOM lock state.
- `memcg1_oom_recover()`: wakes waiters after userspace or limit changes.
- `mem_cgroup_oom_synchronize()`: completes deferred userspace OOM handling at the end of a page fault.

If `oom_kill_disable` is set and the current task is in a user fault, the task stores `current->memcg_in_oom` and sleeps later, after page fault locks are released.

## Limit Updates and Force Empty

`mem_cgroup_resize_max()` updates memory or memsw maximums while preserving the invariant:

`memory.max <= memsw.max`

It drains per-CPU stocks once, attempts reclaim on failure, supports signal interruption, and wakes OOM waiters when limits are enlarged.

`mem_cgroup_force_empty()` drains LRU and stock state, then tries reclaim until the cgroup memory counter reaches zero or retries are exhausted. It backs the legacy `memory.force_empty` file and rejects root cgroup use.

## Legacy File Interface

The file defines `mem_cgroup_legacy_files[]`, the cgroup v1 memory files, including:

- `usage_in_bytes`
- `max_usage_in_bytes`
- `limit_in_bytes`
- `soft_limit_in_bytes`
- `failcnt`
- `stat`
- `force_empty`
- `use_hierarchy`
- `cgroup.event_control`
- `swappiness`
- `move_charge_at_immigrate`
- `oom_control`
- `pressure_level`
- `numa_stat` under `CONFIG_NUMA`
- `kmem.*`
- `kmem.tcp.*`
- `kmem.slabinfo` under `CONFIG_SLUB_DEBUG`

It also defines `memsw_files[]` for:

- `memsw.usage_in_bytes`
- `memsw.max_usage_in_bytes`
- `memsw.limit_in_bytes`
- `memsw.failcnt`

Handlers are dispatched through encoded `cftype.private` values using `MEMFILE_PRIVATE()`, `MEMFILE_TYPE()`, and `MEMFILE_ATTR()`.

Many writes emit deprecation warnings, including soft limits, non-hierarchical mode, move-charge-at-immigrate, `oom_control`, kmem limits, and TCP kmem limits.

## Statistics

`memcg1_stat_format()` emits cgroup v1 `memory.stat` content. It reports:

- local page states such as cache, rss, shmem, dirty, writeback, swap;
- local VM events such as pgpgin, pgpgout, pgfault, pgmajfault;
- local LRU sizes;
- hierarchical memory and memsw effective limits;
- hierarchical totals for the same states and events;
- optional debug VM reclaim cost information.

`reparent_memcg1_state_local()` and `reparent_memcg1_lruvec_state_local()` transfer local v1 stats during memcg reparenting.

Under `CONFIG_NUMA`, `memcg_numa_stat_show()` reports local and hierarchical per-node LRU totals.

## kmem and TCP Memory Accounting

`memcg1_account_kmem()` adjusts the legacy kmem page counter only when memory cgroup is not on the default hierarchy.

`memcg1_charge_skmem()` tries to charge TCP memory, sets `tcpmem_pressure` on failure, and honors `__GFP_NOFAIL` by force-charging.

`memcg_update_tcp_max()` updates the TCP max counter and enables the socket accounting static key before marking `tcpmem_active`.

## Initialization

`memcg1_alloc_events()` allocates per-CPU v1 event counters for a memcg, and `memcg1_free_events()` frees them.

`memcg1_memcg_init()` initializes per-memcg v1 lists and locks for OOM notifications, thresholds, and event registration.

`memcg1_init()` allocates one soft-limit RB-tree node per NUMA node and runs as a `subsys_initcall`.

## Integration Points

This file integrates with:

- `memcontrol.c` core memcg charge and reclaim paths;
- swap cgroup recording;
- page counters;
- VM reclaim and LRU vectors;
- eventfd and poll waitqueues;
- cgroup v1 kernfs file operations;
- vmpressure legacy notifications;
- per-node NUMA memory statistics;
- socket memory accounting static keys.

## Implementation Notes and Risks

This is compatibility-heavy code. Several exposed ABIs are deprecated but still must preserve userspace behavior.

The threshold notification path depends on careful RCU publication and spare-array swapping. The OOM event path depends on spinlock-protected subtree state and asynchronous workqueue cleanup to avoid sleeping from atomic context.

Soft-limit reclaim is explicitly best effort and race tolerant. It should not be treated as a strict enforcement mechanism.

Limit writes must maintain the memory/memsw invariant; violating it would break cgroup v1 memory+swap accounting semantics.
