# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mem_cage.c

## Purpose

Implements the kernel memory cage. The cage reserves and manages relocatable/non-relocatable physical page ranges so kernel memory can remain available while supporting dynamic memory operations and page relocation policies.

It maintains cage ranges, thresholds, free-page accounting, cage expansion, cageout reclaim, allocator throttling, kstats, and memory DR callbacks.

## Main Responsibilities

- Track cage growth ranges with `kcage_glist`.
- Initialize the cage from physical memory lists.
- Mark pages as non-relocatable (`P_NORELOC`) as they enter the cage.
- Reclaim or relocate cage pages under pressure.
- Expand the cage when cage free memory falls below thresholds.
- Throttle page creation when cage memory is scarce.
- Register callbacks for physical memory add/delete threshold recalculation.
- Publish cage ranges through kstat.
- Coordinate cageout thread behavior around CPR suspend/resume.

## Key Data Structures

- `struct kcage_glist`
  Range node with `base`, `lim`, `curr`, and growth direction `decr`. The allocated cage is the consumed part of these monotonic ranges.

- `kcage_glist`
  Head of all cage-eligible ranges.

- `kcage_current_glist`
  Current range being consumed for cage expansion.

- `kcage_range_rwlock`
  Protects range list structure and major range updates.

- Cage thresholds:
  `kcage_freemem`, `kcage_needfree`, `kcage_lotsfree`, `kcage_desfree`, `kcage_minfree`, `kcage_throttlefree`, `kcage_reserve`.

- Cageout synchronization:
  `kcage_cageout_mutex`, `kcage_cageout_cv`, `kcage_cageout_ready`, `kcage_cageout_thread`.

- Throttle synchronization:
  `kcage_throttle_mutex`, `kcage_throttle_cv`.

- Optional `KCAGE_STATS`
  Debug-only scan and event counters for cageout, expansion, throttling, and invalidation.

## Key Entry Points

- `kcage_current_pfn(pfn_t *pfncur)`
  Returns approximate current cage PFN and direction for contiguous page allocation exclusion.

- `kcage_next_range(int incage, pfn_t lo, pfn_t hi, pfn_t *nlo, pfn_t *nhi)`
  Finds the lowest overlapping cage or non-cage range in a PFN interval.

- `kcage_range_init(struct memlist *ml, kcage_dir_t d, pgcnt_t preferred_size)`
  Creates cage arena, builds initial glist from memlist, and calls `kcage_init()`.

- `kcage_range_add()`, `kcage_range_delete()`, `kcage_range_delete_post_mem_del()`
  Dynamic range management APIs.

- `kcage_recalc_thresholds()`
  Recomputes thresholds from `total_pages` and configured initial values, wakes cageout/throttled waiters when needed.

- `kcage_cageout_init()`
  Starts cageout LWP under `proc_pageout` if cage is enabled.

- `kcage_create_throttle(pgcnt_t npages, int flags)`
  Blocks or classifies page creation requests depending on cage free memory, real-time priority, panic/cageout context, VM criticality, and wait flags.

- `kcage_freemem_add()` / `kcage_freemem_sub()`
  Atomic cage free-memory accounting and wakeup trigger points.

- `kcage_cageout_wakeup()`
  Signals cageout thread or performs early expansion before cageout is ready.

- `kcage_tick()`
  Periodic safety wakeup for throttled threads.

## Internal Algorithms

### Range Management

`kcage_range_add_internal()` creates a new glist node and deletes overlaps from the new range before appending it. `kcage_glist_delete()` supports whole-range removal, front/back trimming, and middle splits. Deletion refuses ranges overlapping already-used cage portions unless called from post-memory-delete cleanup.

### PFN Allocation

`kcage_get_pfn()` consumes PFNs from `kcage_current_glist`, growing either upward or downward. It advances to the next range when the current range is exhausted.

`kcage_walk_cage()` walks the static allocated portion of the cage in ascending PFN order for cageout scans.

### Initialization

`kcage_init()` recalculates preferred size, registers kphysm callbacks, chooses startup cage size bounded by `kcage_minfree` and `availrmem`, marks startup cage pages `P_NORELOC`, captures existing kernel allocated pages from `kvp.v_pages`, enables `kcage_on`, registers CPR callback, optionally coalesces free pages for large pages, and installs raw kstat reporting.

### Assimilation and Reclaim

`kcage_assimilate_page()` tries to lock a page, mark it non-relocatable, and either move a free page to the correct NORELOC list or invalidate/relocate an allocated page.

`kcage_invalidate_page()` unloads mappings, checks lock/COW/modified state, relocates if required, demotes large pages when possible, and disposes clean unshared pages.

`kcage_expand()` consumes new PFNs from the glist until enough free caged pages exist or expansion cannot progress.

`kcage_cageout()` scans caged pages, assimilates holes, skips pages it cannot safely lock or pages with excessive sharing, invalidates/relocates pages, expands if still under throttle threshold, and broadcasts to throttled allocators.

## Locking and Synchronization

- Range list edits require `kcage_range_rwlock` writer lock.
- Read-side range queries tolerate some `curr` movement races by design.
- Cageout waits on `kcage_cageout_cv` under `kcage_cageout_mutex`.
- Throttled allocators wait on `kcage_throttle_cv` under `kcage_throttle_mutex`.
- `kcage_freemem` and `kcage_needfree` use atomics in some startup paths.
- Page-level operations depend on page locks, group page locks, HAT unload synchronization, and free-list manipulation rules.

## External Dependencies

VM page allocator, page relocation, HAT, page free/cache lists, kphysm setup callbacks, CPR callbacks, kstats, lgrp, segkmem large page settings, pageout scanner, and memory deletion state via `pfn_is_being_deleted()`.

## Research Notes

The cage is a pressure-control subsystem with subtle accounting. Key invariants are: `P_NORELOC` pages must be on appropriate accounting lists, cage expansion must not enter memory being deleted, cageout must not block itself, and throttled allocators must eventually be woken even if reclaim makes no forward progress.
