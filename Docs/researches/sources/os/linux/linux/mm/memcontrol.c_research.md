# File Research: sources/os/linux/linux/mm/memcontrol.c

## Role

Main Linux memory controller implementation for the cgroup memory subsystem. It defines the `memory_cgrp_subsys`, root memory cgroup, per-memcg/per-node accounting, folio and kernel-object charging, memory/swap/zswap limits, reclaim throttling, memcg OOM handling, lifecycle hooks, rstat flushing, cgroupfs files, socket memory accounting, and integration with writeback, LRU generations, shrinkers, hugetlb, swap, and cgroup v1 compatibility.

## Key Behavior

- Initializes global memcg state, per-CPU charge stocks, object charge stocks, workqueues, slab caches, stats indexes, VM event indexes, CPU hotplug drain handling, and boot options from `cgroup.memory=` and `swapaccount=`.
- Allocates and onlines memcgs through cgroup CSS hooks, including page counters, per-node `lruvec` state, vmstats, private 16-bit memcg IDs, vmpressure, memory peaks, writeback domains, shrinker state, objcg roots, and LRU generation state.
- Offlines and frees memcgs by clearing protection limits, cleaning zswap state, reparenting list_lru/deferred split/object cgroups, invalidating reclaim iterators, waiting for foreign writeback completions, draining per-CPU stocks, releasing private IDs, and freeing per-node/per-CPU storage.
- Maintains per-memcg and per-lruvec statistics through per-CPU deltas, cgroup rstat propagation, periodic flush work, synchronous flush-on-read thresholds, NMI-safe atomic fallbacks, and v1 local-stat reparenting.
- Implements page/folio charging through `try_charge_memcg()`: consumes per-CPU stock, attempts memory and memsw page-counter charges, handles `memory.max` events, reclaim, stock draining, retry policy, memcg OOM, forced charges for nofail/high-priority allocations, and `memory.high`/`swap.high` overage notification.
- Enforces `memory.high` with reclaim and exponential task throttling on user-return paths via `__mem_cgroup_handle_over_high()`, plus async high-limit work for interrupt-context charges.
- Tracks folio ownership through `folio->memcg_data` carrying an objcg, with helpers for normal charge, hugetlb charge, swapin charge, batched uncharge, replacement, migration, folio split reference propagation, and procfs inode lookup.
- Accounts kernel memory and slab objects with `obj_cgroup` references, per-task lazy objcg caching, per-CPU byte stock, slab object extension storage, list_lru preallocation, per-node slab vmstat batching, NMI-safe accounting paths, and object-cgroup reparenting on memcg removal.
- Provides socket memory accounting on cgroup v2 and v1, including socket memcg association, inheritance, charge/uncharge, and static-key enablement.
- Supports cgroup writeback by exposing memcg writeback domains, per-writeback dirty/writeback/headroom stats, foreign dirty tracking, and remote foreign writeback flushing for inode/page ownership mismatches.
- Maintains private memcg IDs for swap and shadow entries so IDs can be recycled after cgroup offlining while referenced pages can still resolve to live ancestors.
- Exposes cgroup v2 memory files: `memory.current`, `memory.peak`, `memory.min`, `memory.low`, `memory.high`, `memory.max`, `memory.events`, `memory.events.local`, `memory.stat`, optional `memory.numa_stat`, `memory.oom.group`, and `memory.reclaim`.
- Under `CONFIG_SWAP`, exposes `memory.swap.current`, `memory.swap.high`, `memory.swap.max`, `memory.swap.peak`, and `memory.swap.events`; records swap cgroup IDs, charges/un-charges swap, computes per-memcg swap availability, and detects swap-full conditions.
- Under `CONFIG_ZSWAP`, enforces hierarchical zswap limits, charges/un-charges compressed backend memory, tracks zswap stats, controls zswap writeback, and exposes `memory.zswap.current`, `memory.zswap.max`, and `memory.zswap.writeback`.
- Preserves cgroup v1 behavior through `memcontrol-v1.h` helpers for legacy files, soft limits, kmem/tcp accounting, non-hierarchical local stats, OOM preparation/finish, and legacy stat formatting.

## Dependencies

Uses cgroup core, `page_counter`, folio/page cache helpers, reclaim/vmscan, swap cgroup, shmem/hugetlb, slab object extensions, list_lru, shrinkers, LRU generations, rstat, vmpressure, PSI, OOM, cpuset, socket memory hooks, writeback domains, zswap, tracepoints from `trace/events/memcg.h` and `trace/events/vmscan.h`, and legacy memcg-v1 support.

## Research Notes

This file is the central policy and accounting layer for memory isolation. The implementation is intentionally split between fast-path approximate per-CPU accounting and slower synchronized reconciliation: charges use stocks and deferred rstat propagation for performance, while limit changes, OOM paths, swap/zswap decisions, and user-visible stats force draining or flushing when accuracy is required. The highest-risk invariants are ownership lifetime (`obj_cgroup` and private memcg IDs), charge/uncharge pairing across folio migration/replacement/swap, lock ordering during objcg reparenting, and limit enforcement behavior under reclaim, OOM, and dying-task conditions.
