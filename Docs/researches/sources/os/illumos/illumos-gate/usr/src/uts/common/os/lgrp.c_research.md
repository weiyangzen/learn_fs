# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/lgrp.c

## Purpose

`lgrp.c` implements illumos kernel locality-group support. Lgroups describe NUMA locality between CPUs and memory, drive scheduler homing, guide memory placement, maintain per-lgroup load averages and kstats, and handle CPU/memory dynamic reconfiguration.

The file also maintains per-CPU-partition lgroup load structures, known as `lpl_t`, which mirror usable portions of the lgroup topology for dispatcher decisions.

## Global State

Core topology state:

- `lgrp_gen`: generation counter for topology/resource changes.
- `lgrp_table[]`: indexed table of initialized or recyclable `lgrp_t` objects.
- `nlgrps`, `nlgrpsmax`, `lgrp_alloc_hint`, `lgrp_alloc_max`.
- `lgrp_root`: root locality group.
- `lgrp_initialized` and `lgrp_topo_initialized`.

Bootstrap scheduler state:

- `lpl_bootstrap_list`, `lpl_bootstrap`, and associated bootstrap resource arrays allow CPU0 and early slave CPUs to use minimal lpl state before `cp_default` is fully initialized.

Memory placement tunables include private/shared random thresholds, default/root policies, processor-set awareness, and segmap policy.

## Initialization

`lgrp_init()` is staged and delegates platform initialization through `lgrp_plat_init()`:

- stage 1 sets `nlgrpsmax`
- stage 2 runs `lgrp_setup()`
- stage 4 runs `lgrp_main_init()`
- stage 5 runs `lgrp_main_mp_init()`

`lgrp_root_init()` creates the root lgroup, initializes bootstrap lpl state, and sets `t0.t_lpl`.

`lgrp_setup()` creates the root, adds CPU0, and marks CPU0 online through `lgrp_config()`.

`lgrp_main_init()` validates memory policy defaults, handles platform cases that collapse topology to UMA, initializes kstats, creates CPU0 kstats, and marks lgroup initialization complete.

`lgrp_main_mp_init()` initializes SMT support, finishes topology updates after all CPUs are online, and marks topology initialization complete.

## Reconfiguration

`lgrp_config()` handles common lgroup events:

- CPU add/delete/online/offline
- CPU partition add/delete
- memory add/delete/rename
- generation bump
- topology flatten
- latency changes

CPU online initializes the CPU’s lgroup, adds it to its CPU partition’s lpl topology, verifies the lpl topology, informs platform code, and increments `lgrp_gen`. CPU offline removes partition and lgroup membership, verifies topology, informs platform code, and increments `lgrp_gen`.

Memory add/remove uses `lgrp_mem_init()` and `lgrp_mem_fini()`. Memory rename is modeled as remove-from-source followed by add-to-destination, with special handling for DR copy-rename cases where temporarily removing the last memory node from root could make allocations fail.

## Lgroup Object Lifecycle

`lgrp_create()` allocates or recycles an `lgrp_t`, assigns an ID, clears topology/resource state, resets kstats if needed, and stores it in `lgrp_table`.

`lgrp_destroy()` marks an lgroup reusable by setting `lgrp_id` to `LGRP_NONE`, clearing parent/child/resource/memory/CPU state, updating allocation hints, and decrementing `nlgrps`. Lgroup structures are recycled rather than always freed.

## CPU And Memory Resource Management

`lgrp_cpu_init()` maps a CPU to a platform lgroup handle, creates or updates the leaf lgroup as needed, adds CPU resources to the topology, updates memory nodes for changed intermediate groups, assigns `cpu_lpl`, and links the CPU into the lgroup CPU circular list.

`lgrp_cpu_fini()` removes a CPU from the lgroup CPU list. If the last CPU leaves a leaf lgroup, CPU resources are removed; if no resources remain, the leaf is removed from the topology.

`lgrp_mnode_update()` recomputes memory-node sets for target lgroups based on their memory resource sets.

`lgrp_mem_init()` adds a memory node to an existing or newly created lgroup, updates topology under `cpu_lock`, pauses CPUs when needed, and updates changed ancestor memory-node sets.

`lgrp_mem_fini()` removes a memory node, clears memory resources if an lgroup no longer has memory, and deletes empty leaf lgroups when needed.

## Queries And Kstats

Query helpers include:

- `lgrp_home_lgrp()`
- `lgrp_home_id()`
- `lgrp_pfn_to_lgrp()`
- `lgrp_phys_to_lgrp()`
- `lgrp_hand_to_lgrp()`
- `lgrp_query_cpu()`
- `lgrp_query_load()`
- `lgrp_mem_size()`

Kstat support initializes named stats, creates per-lgroup kstats, resets counters, extracts counter and snapshot values, and reports CPU count, installed/available/free pages, and load average.

## LPL Topology

The lpl layer stores CPU-partition-specific load and resource hierarchy data. It uses `lpl_t` records indexed by lgroup ID inside each `cpupart_t`.

Main lpl operations:

- `lpl_init()` and `lpl_clear()`
- `lpl_rset_add()` and `lpl_rset_del()`
- `lpl_leaf_insert()` and `lpl_leaf_remove()`
- `lgrp_part_add_cpu()` and `lgrp_part_del_cpu()`
- `lpl_topo_verify()`
- `lpl_topo_flatten()`
- `lpl_topo_bootstrap()`

`lpl_topo_verify()` is extensive. It checks lpl/lgroup ID correspondence, parent consistency, leaf CPU lists and counts, non-leaf resource counts, resource-set membership, partition membership, orphaned lpls, and CPU-to-lpl pointers.

## Load And Thread Homing

`lgrp_loadavg()` updates a leaf lpl and its ancestors using a fixed-point exponential decay. It supports both normal aging updates and anticipatory remote-thread load increments.

`lgrp_choose()` selects a home lgroup for a thread within a CPU partition. It considers explicit lgroup affinity, partition membership, leaf-only placement, free-memory thresholds, process spread, load thresholds, expansion thresholds, and policy mode:

- random
- round-robin
- longest time since last homed

`lpl_pick()` compares two candidate lpls using load and tolerance.

`lgrp_move_thread()` is the sole routine that updates a thread’s `t_lpl`. It updates process lgroup membership, migration counters, text-replication migration tracking, and anticipatory load on the new lgroup and its ancestors. It can also remove recently added anticipatory load if the old placement was too short-lived.

## Memory Policy

Memory placement policies handled here include:

- default / next-touch
- next CPU
- random across machine
- random across process lgroups
- random across processor-set lgroups
- round-robin
- next segment

`lgrp_mem_policy_default()` decides default policy based on mapping type, size, thresholds, and processor-set awareness.

`lgrp_mem_choose()` selects the lgroup for allocation based on segment policy, current thread home, root override behavior, random/round-robin logic, and DR tolerance.

Shared memory policy support stores per-range policy in AVL trees attached to `anon_map` or vnode locality structures. Functions include initialization/finalization, AVL comparison, split/concat, lookup, and `lgrp_shm_policy_set()`.

`lgrp_memnode_choose()` chooses actual memnodes from an lgroup, optionally traversing ancestors when local nodes are exhausted.

## Concurrency

Important rules:

- `cpu_lock` protects most topology mutations after initialization.
- Some paths run with CPUs paused and must not block or acquire new locks.
- `kpreempt_disable()` protects reads of current CPU/thread lpl state where needed.
- Shared memory policy trees use `loc_lock`.
- Kstat extraction uses `lgrp_kstat_mutex`.
- Load averages are updated atomically.

## Dependencies

Depends on platform lgroup callbacks, CPU and CPU partition code, scheduler structures, memnode support, VM segment policies, AVL trees, kstats, processor groups, SMT initialization, DTrace probes, and page/memory sizing hooks.

## Research Notes

The highest-risk areas are DR memory remove/add edge cases, lgrp/lpl topology consistency, anticipatory load accounting, CPU partition transitions, shared-memory policy range splitting/concatenation, and calls made while CPUs are paused where blocking would be unsafe.
