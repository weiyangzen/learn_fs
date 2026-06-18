# File Research: sources/os/linux/linux/mm/workingset.c

## Purpose

`workingset.c` implements Linux workingset detection for page cache and anonymous memory refaults. It records eviction timestamps in xarray shadow entries, compares later refault distance against active/inactive memory dimensions, and decides whether a refaulting folio should be activated or restored as part of the working set. It also maintains and shrinks shadow-entry xarray nodes to prevent unbounded metadata growth.

The core idea is that the distance between eviction and refault approximates how much inactive-list space the page would have needed to remain resident. If that distance fits within the current workingset, activation is worthwhile.

## Shadow Entry Encoding

Shadow entries are xarray value entries produced by `pack_shadow()` and decoded by `unpack_shadow()`. They store:

- memcg private ID
- NUMA node ID
- eviction timestamp or multigenerational LRU token
- whether the evicted folio had `workingset` state

Bit allocation is constrained by `BITS_PER_XA_VALUE`, `NODES_SHIFT`, and `MEM_CGROUP_ID_SHIFT`. `bucket_order[WORKINGSET_FILE]` and `bucket_order[WORKINGSET_ANON]` reduce timestamp granularity when physical memory is larger than the available timestamp range.

## Classic LRU Workingset Flow

`workingset_eviction()` is called for a locked, fully exclusive folio being evicted. It reads the reclaiming lruvec's `nonresident_age`, buckets the value, ages the nonresident counter by the folio size, and returns a packed shadow entry.

`workingset_test_recent()` decodes a shadow entry, resolves the memcg and node lruvec, computes `refault_distance = refault_age - eviction_age` with masked unsigned arithmetic, and compares that distance with the relevant active and inactive list sizes. File and anon refaults use slightly different comparisons, and anon/file competition depends on available swap. It can flush memcg stats unless called from a context that cannot sleep.

`workingset_refault()` handles a newly allocated locked folio and a matching shadow entry. It records refault stats, tests recency, activates the folio if appropriate, ages nonresident state, and restores `workingset` state plus refault cost if the evicted folio had been active.

`workingset_activation()` advances nonresident age on folio activation, including ancestor lruvecs, so nonresident and resident LRU ages remain comparable.

## Multigenerational LRU Integration

When `CONFIG_LRU_GEN` is enabled:

- `lru_gen_eviction()` records generation sequence and reference tier in the shadow token and updates generation eviction histograms.
- `lru_gen_test_recent()` treats a token as recent if its generation sequence is within `MAX_NR_GENS`.
- `lru_gen_refault()` updates refault histograms, activation stats, and either restores workingset state or reference bits for the refaulting folio.

When multigenerational LRU is disabled, those helpers compile to stubs and the classic nonresident-age distance algorithm is used.

## Shadow Node Reclaim

Shadow entries occupy xarray nodes after folios are evicted. `workingset_update_node()` maintains the global `shadow_nodes` `list_lru`: a node is listed when all entries are values and no real folios remain. It increments or decrements `WORKINGSET_NODES`.

`count_shadow_nodes()` computes reclaimable shadow-node pressure. It caps shadow metadata based on either memcg lruvec size plus slab or node present pages, using a worst-case density compromise so shadow nodes do not consume excessive memory for streaming workloads.

`shadow_lru_isolate()` reclaims one shadow-only xarray node. It inverts lock order carefully by first holding the list_lru lock, then trylocking `mapping->i_pages`, and for page cache mappings also trylocking the inode lock. It validates that the node contains only values, deletes the node with `xa_delete_node()`, records `WORKINGSET_NODERECLAIM`, and requeues shrinkable inodes as needed.

`scan_shadow_nodes()` wires this into `list_lru_shrink_walk_irq()`.

## Initialization

`workingset_init()` computes timestamp bucket orders, logs the resulting bit budget, allocates a NUMA-aware and memcg-aware shrinker named `mm-shadow`, initializes `shadow_nodes` with a lock class key, assigns count and scan callbacks, and registers the shrinker.

## Integration Points

This file is used by reclaim, page cache, swap, memcg, xarray, list_lru, and lruvec statistics. Its counters are reported through vmstat names such as `workingset_refault_*`, `workingset_activate_*`, `workingset_restore_*`, `workingset_nodes`, and `workingset_nodereclaim`.

## Concurrency And Invariants

- Eviction folios must be locked, refcount-free, and off LRU when shadow entries are created.
- Refault folios must be locked so memcg ownership is stable.
- Deleted memcgs can make a shadow entry unusable; recycled IDs are tolerated as rare speculative noise.
- Shadow-node list updates require the xarray lock.
- Shadow-node reclaim relies on lock try-acquisition and retry status to avoid deadlocks with page cache and inode locking.

## Risks And Test Focus

Risks include shadow bitfield overflow, timestamp bucket miscalculation on large memory systems, incorrect memcg ref handling, stale shadow entries causing false activations, and xarray/list_lru locking regressions. Tests should stress memcg deletion/reuse, swap availability differences, file versus anon refaults, `CONFIG_LRU_GEN` and non-LRU_GEN builds, shadow-node shrinker pressure, and concurrent page-cache insertion/deletion.
