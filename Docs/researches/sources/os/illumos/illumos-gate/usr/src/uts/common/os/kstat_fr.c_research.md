# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kstat_fr.c

## Purpose

`kstat_fr.c` implements the core illumos kernel statistics framework. It creates, indexes, installs, snapshots, updates, zones, deletes, and times kstats exposed through `/dev/kstat`, including foundational system, VM, page, poll, and I/O timing statistics.

Read completely: 1,455 lines.

## Main Responsibilities

- Maintains global kstat AVL indexes by KID and by module/instance/name/zone visibility.
- Assigns and increments `kstat_chain_id` so `/dev/kstat` consumers can detect chain changes.
- Supports zone visibility lists for kstats visible to all zones, selected zones, or zone-specific readers.
- Allocates kstat headers and optional physical data from a boot-time buffer and later from a `vmem` arena.
- Initializes built-in kstats such as `kstat_headers`, `kstat_types`, `sysinfo`, `vminfo`, `segmap`, `biostats`, `var`, `system_misc`, `system_pages`, and `pollstats`.
- Provides default update and snapshot routines, including long-string named kstat support and I/O time normalization.
- Creates, installs, deletes, dormants, reactivates, and deletes-by-name kstats.
- Provides queue/timer accounting helpers for kstat I/O and event-timer users.

## Important Data Structures And Globals

- `ekstat_t`: private wrapper around `kstat_t`, adding allocation size, owner thread, wait CV, AVL nodes, and a zone visibility list.
- `kstat_zone_t`: singly linked zone ID list for visibility checks.
- `kstat_chain_lock`: protects AVL trees and `kstat_chain_id`.
- `kstat_chain_id`: monotonically updated chain/KID source, reserved initially for well-known kstats.
- `kstat_initial` / `kstat_initial_ptr` / `kstat_initial_avail`: early boot allocation pool before the kstat arena exists.
- `kstat_arena`: later vmem arena for kstat allocations.
- `kstat_avl_bykid` and `kstat_avl_byname`: primary lookup indexes.
- `kstat_data_type[]`: type descriptors for raw, named, interrupt, I/O, and event-timer kstats.
- `system_misc_kstat` and `system_pages_kstat`: built-in named-stat backing storage updated dynamically.

## Zone Visibility

The file models three kstat visibility classes: well-known kstats whose data changes per reading zone, kstats exported to a specific list of zones, and kstats visible to all zones. `kstat_zone_find()` accepts `ALL_ZONES` matches or exact zone IDs. `kstat_zone_add()` and `kstat_zone_remove()` mutate a kstat's visibility list and bump `kstat_chain_id`, treating visibility changes like install/delete events for userland chain consumers.

AVL comparison includes zone comparison after KID or name equality, so a name lookup is effectively module/instance/name/visible-zone. Non-global zones are disallowed from writing kstats by framework policy.

## Lookup And Ownership

`kstat_hold()` is the shared hold primitive for both AVL indexes. It searches under `kstat_chain_lock`, waits if another thread owns the matching `ekstat_t`, then records `curthread` as owner. `kstat_rele()` clears ownership and broadcasts waiters. Public lookup wrappers are `kstat_hold_bykid()` and `kstat_hold_byname()`.

This owner field serializes framework operations on an individual kstat without holding the chain lock across provider update/snapshot work.

## Allocation And Initialization

`kstat_alloc()` rounds each allocation to `KSTAT_ALIGN` and uses `kstat_initial` before `kstat_arena` exists. Once `kstat_init()` creates the arena, it reserves the initial allocations in vmem using `vmem_xalloc()` so early kstats become accounted arena allocations.

`kstat_init()` creates the kstat arena and installs the foundational kstats. `kstat_headers` is KID 0 and exposes the header chain itself; `kstat_types` enumerates type IDs. Several virtual kstats point directly at kernel structures or externally maintained named arrays.

## Creation, Install, Delete

`kstat_create()` delegates to `kstat_create_zone()` with `ALL_ZONES`. `kstat_create_zone()` validates type, persistent/virtual incompatibility, variable-size physical restrictions, and legal `ks_ndata`; synthesizes a name when `ks_name` is NULL; handles namespace collision; and reactivates matching dormant kstats when parameters are compatible.

New kstats are inserted invalid into both AVL trees, assigned the next unused KID from `kstat_chain_id`, and initialized with default update/snapshot handlers. `kstat_install()` verifies variable-size locking, detects named long strings, rejects writable long-string named kstats that rely on the default snapshot routine, rehydrates dormant persistent kstats through a write update, then clears `KSTAT_FLAG_INVALID` under the chain lock.

`kstat_delete()` refuses deletion while the caller holds the provider data lock. Persistent kstats are updated one last time, marked dormant, and reset to default framework handlers. Nonpersistent kstats are removed from both AVL trees, chain ID is bumped, zone-list allocations are freed, the hold is released, and memory is returned to the arena.

## Snapshot And Update

`default_kstat_update()` recalculates `ks_data_size` for variable-size named kstats with long strings. `default_kstat_snapshot()` handles write permissions, copies data, normalizes `KSTAT_TYPE_IO` unscaled times, accounts for in-progress wait/run queue transactions, and copies variable-length named strings into the snapshot buffer while rewriting their pointers to point inside that buffer.

`header_kstat_update()` counts visible, non-invalid kstats for the current zone and sets the header data size. `header_kstat_snapshot()` copies visible kstat headers in increasing KID order while the chain lock is held, matching the `/dev/kstat` two-pass contract.

## Built-In System Kstats

`system_misc_kstat_update()` reports CPU count, lbolt, deficit, clock interrupts, VAC state, process count, load averages, boot time, and nanoseconds per tick. For non-global zones, it uses pool pset CPU count when enabled, zone load averages, zone boot time, zone-relative lbolt, and zone process count.

`system_pages_kstat_update()` reports memory and VM page values such as `physmem`, kernel module allocation counts from `kobj_stat_get()`, `freemem`, `availrmem`, page scanner thresholds, `pagesfree`, `pageslocked`, `pagestotal`, low-memory scan/throttle counters, and `pp_kernel` derived from installed memory minus boot/kernel/user-lock reservations.

## Queue And Timer Accounting

The non-SPARC C implementations of `kstat_waitq_enter()`, `kstat_waitq_exit()`, `kstat_runq_enter()`, `kstat_runq_exit()`, `kstat_waitq_to_runq()`, and `kstat_runq_back_to_waitq()` update unscaled timestamps, queue counts, elapsed queue time, and length-time integrals. `default_kstat_snapshot()` later scales these for users.

`kstat_timer_start()` records a high-resolution start time. `kstat_timer_stop()` updates stop time, elapsed event duration, min/max duration, cumulative elapsed time, and event count.

## Notable Risks And Invariants

- The header kstat update/snapshot pair assumes `kstat_chain_lock` is held across sizing and copyout to prevent chain growth from overrunning the caller's buffer.
- Variable-size kstats must provide `ks_lock`; `kstat_install()` panics if they do not.
- Persistent virtual kstats are rejected because the provider backing pointer would become invalid after provider unload.
- Writable named kstats containing long strings must provide a custom snapshot routine.
- Zone visibility changes bump the chain ID, which can surprise readers that treat only install/delete as chain changes.

## Research Relevance

For filesystem and storage research, kstats are the primary kernel telemetry surface for VFS, disk, NFS, ZFS, VM, page cache, and allocator behavior. This file defines the concurrency, snapshot, zone visibility, and persistent-stat contracts that storage subsystems rely on when publishing metrics.
