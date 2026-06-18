# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/callout.c

## Purpose

`callout.c` implements illumos timeout/callout scheduling. It supports legacy `timeout(9F)` IDs and full callout IDs, per-CPU normal and realtime callout tables, cyclic-based expiration, taskq execution for normal callouts, high-resolution grouping, cancellation, CPU online/offline migration, CPR suspend/resume, debugger time adjustment, and hrestime changes.

## Main Interfaces

Creation/cancellation: `timeout_generic`, `timeout`, `timeout_default`, `realtime_timeout`, `realtime_timeout_default`, `untimeout_generic`, `untimeout`, `untimeout_default`.

Expiration paths: `callout_realtime`, `callout_queue_realtime`, `callout_normal`, `callout_queue_normal`, `callout_execute`, `callout_hrestime`.

Lifecycle: `callout_init`, `callout_mp_init`, `callout_cpu_online`, `callout_cpu_offline`.

Private machinery covers callout/list allocation, list lookup, heap insert/delete/process, queue insert/delete/process, cyclic setup, kstats, CPR/debug callbacks, and expired-list execution.

## Behavior

Each CPU has realtime and normal callout tables. Realtime callouts execute from low-level cyclic context. Normal callouts are noticed by a cyclic handler at lock PIL and executed by a per-table taskq at thread context.

Callouts are grouped by exact expiration into `callout_list_t` objects. Lists are indexed by expiration hash, tracked in a min-heap when possible, and placed in a sorted queue if heap expansion fails. A separate ID hash table supports cancellation.

`timeout_generic()` computes expiration, applies resolution/rounding, chooses an ID format, finds or creates a matching callout list, inserts the list into the heap or queue, appends the callout to the list and ID hash, and updates pending counters.

`untimeout_generic()` locates an ID, removes unexpired callouts, waits for currently executing callouts unless `nowait` or self-cancel applies, and returns remaining time or `-1`.

Expiration proceeds in two phases: expired lists are moved to `ct_expired`, then `callout_expire()` invokes each callback, frees callout records to the table freelist, and wakes waiters.

## Time And CPU Handling

Heap processing cleans empty lists, adjusts relative callouts after debugger pauses, and expires absolute hrestime callouts after system time changes. CPR suspend reprograms cyclics to infinity; resume processes time changes and reprograms earliest expirations.

CPU online creates lgroup-local kmem caches, initializes table heaps/hashes/kstats/cyclics, creates taskqs for normal tables, and binds cyclics to the CPU. CPU offline unbinds cyclics so the cyclic subsystem can move them.

## Notable Invariants

- `ct_mutex` protects all table-local callout/list/heap/hash state.
- Callout structures and lists are persistent and recycled, not normally destroyed.
- `CALLOUT_EXECUTING` in `c_xid` coordinates `untimeout()` with active callbacks.
- Empty heaped lists are lazily reaped through `ct_nreap`.
- Normal callouts may need multiple taskq executor threads to avoid dependency deadlocks.
- Realtime handlers must avoid paths such as `cpu_lock` that can deadlock CPU offline.

## Dependencies

Depends on cyclic subsystem, taskq, CPU online/offline, kmem caches, lgroup handles, kstats, CPR callbacks, debugger callbacks, DTrace probes, and callout ID macros from `sys/callo.h`.

## Research Notes

Audit hotspots include ID generation/wrap semantics, cancellation while executing, heap cleanup and queue fallback correctness, cyclic reprogramming under suspend/offline, normal-callout taskq dispatch guarantees, and absolute hrestime expiration on clock changes.
