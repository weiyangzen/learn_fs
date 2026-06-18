# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/metaslab.c

## Scope

This file implements the core ZFS metaslab allocator for illumos: metaslab classes, metaslab groups, per-metaslab range-tree state, allocator policies, weight/fragmentation scoring, allocation and free paths, sync-time spacemap persistence, log spacemap flushing, checkpoint accounting, indirect-vdev remapping, and allocation throttling. The file was read completely.

## APIs And Entry Points

- Lifecycle and stats: `metaslab_stat_init()`, `metaslab_stat_fini()`, `metaslab_init()`, `metaslab_fini()`, `metaslab_load()`, `metaslab_unload()`, `metaslab_load_wait()`, `metaslab_flush_wait()`.
- Class/group management: `metaslab_class_create()`, `metaslab_class_destroy()`, `metaslab_class_validate()`, class space getters, `metaslab_class_fragmentation()`, `metaslab_class_expandable_space()`, `metaslab_class_evict_old()`, `metaslab_group_create()`, `metaslab_group_destroy()`, `metaslab_group_activate()`, `metaslab_group_passivate()`, `metaslab_group_initialized()`, `metaslab_sync_reassess()`.
- Allocation: `metaslab_alloc()`, `metaslab_alloc_dva()`, `metaslab_group_alloc()`, `metaslab_group_alloc_normal()`, `metaslab_block_alloc()`, plus dynamic-fit, cursor-fit, and new-dynamic-fit allocator ops.
- Free/claim/remap: `metaslab_free()`, `metaslab_free_dva()`, `metaslab_free_concrete()`, `metaslab_unalloc_dva()`, `metaslab_claim()`, `metaslab_claim_impl()`, `spa_remap_blkptr()`.
- Sync/persistence: `metaslab_sync()`, `metaslab_sync_done()`, `metaslab_flush()`, `metaslab_set_unflushed_txg()`, `metaslab_unflushed_txg()`.
- Debug/support: allocation tracing, `metaslab_check_free()`, histogram verification, disabled-metaslab controls, allocation-throttle reserve/unreserve helpers.

## Control Flow

Metaslab classes represent allocation classes such as normal, special, or dedup and maintain a rotor of active metaslab groups. Groups represent top-level vdev allocation domains and maintain an AVL tree of metaslabs sorted by active state and weight. Group eligibility is recalculated from vdev free capacity, fragmentation, activation state, and allocation throttle queue depth.

Each metaslab has multiple range trees for distinct TXG states: currently allocatable space, allocations in each TXG, frees being synced, freed/deferred frees, checkpointing, unflushed alloc/free deltas, and trim candidates. `metaslab_init()` creates the metaslab object, opens an existing spacemap if present, creates the initial allocatable/trim trees, joins the group, and initializes space accounting when the metaslab is immediately available. `metaslab_sync_done()` lazily creates the remaining TXG trees for newly available metaslabs.

Loading a metaslab reads its space map up to `ms_synced_length`, builds the in-core allocatable tree and size-sorted auxiliary tree, applies unflushed deltas, removes deferred/freed ranges that are not usable yet, recalculates weight, and updates `ms_max_size`. Loading coordinates with `ms_loading`, `ms_flushing`, and `ms_sync_lock` because sync, flush, and load may all touch related on-disk and in-core state.

Allocation begins at the class rotor, selects candidate metaslab groups with capacity/fragmentation/throttle filtering, then selects or activates a metaslab. Active metaslabs are tracked per allocator as primary or secondary; claim activation is separate for import/ZIL claim paths. The selected allocation policy removes a range from `ms_allocatable`, records it in the current TXG’s `ms_allocating` tree, clears overlapping trim candidates, dirties the metaslab, and updates queue-depth tracking.

Sync writes TXG allocation/free deltas either to the pool-wide log spacemap or directly to the metaslab spacemap. It updates allocated-space counters, checkpoint spacemaps, histograms, auxiliary histograms, unflushed delta trees, and deferral state. `metaslab_sync_done()` returns deferred frees to circulation when allowed, updates class/vdev accounting, recalculates weight, and unloads old inactive metaslabs. `metaslab_flush()` writes accumulated log-spacemap deltas back into a metaslab’s own spacemap; if the metaslab should condense, it rewrites a compact spacemap instead.

Freeing validates the target DVA, routes indirect vdev mappings through `vdev_op_remap`, handles removing-vdev obsolete accounting, and adds concrete ranges to `ms_freeing` or `ms_checkpointing`. Immediate unallocation removes the range from `ms_allocating` and returns it to `ms_allocatable`. Claim paths dry-run first, then remove claimable ranges from free space and dirty allocation state.

## State And Dependencies

The file depends heavily on `range_tree.c`, space maps, DMU transactions, SPA config locks, vdev state, ZIO allocation flags, blkptr/DVA helpers, AVL trees, btrees, multilists, and ZFS feature flags such as spacemap histograms, log spacemap, obsolete counts, and checkpoints.

Important state includes class counters (`mc_alloc`, `mc_deferred`, `mc_space`, histograms, rotor, allocation slots), group state (`mg_metaslab_tree`, primaries/secondaries, allocatable flags, fragmentation, disabled counts, queue-depth refcounts), and per-metaslab state (`ms_allocatable`, TXG trees, unflushed trees, `ms_weight`, `ms_fragmentation`, `ms_max_size`, loading/flushing/condensing flags, spacemap object, deferred-space accounting).

## Risks And Invariants

- Lock ordering is critical. The code uses spa config locks, group locks, metaslab locks, `ms_sync_lock`, multilist sublist locks, and disabled-metaslab locks with carefully documented drop/reacquire points.
- Loaded and unloaded metaslabs intentionally compute weights from different sources: loaded range-tree histograms versus on-disk spacemap histograms adjusted by auxiliary defer histograms.
- Log spacemap mode changes load, sync, and flush behavior. Incorrect unflushed delta handling can double-count or lose allocations/frees.
- `ms_condensing` prevents allocations while compacting a spacemap because the in-core free tree is being committed in a special form.
- Free deferral is bypassed near slop space or during vdev removal, which changes when freed space returns to allocatable state.
- Indirect vdev remapping intentionally avoids dedup, gang, embedded, and split-block cases; remapping changes DVA[0] and physical birth.
- Allocation throttling uses debug refcounts and per-vdev queue depth; failures for gang block minimum size mark groups as having no free space.
- Metaslab disable/enable limits the number of disabled metaslabs per group to avoid total allocation starvation during initialize/TRIM work.

## Summary

`metaslab.c` is the illumos ZFS allocator’s central implementation. It converts pool/vdev free-space metadata into weighted metaslab selection, performs allocation and free bookkeeping across TXGs, persists that bookkeeping through space maps and log space maps, and coordinates with checkpoints, vdev removal, trim, gang allocation, and import-time claiming. Its highest-risk areas are concurrency, on-disk/in-core space accounting consistency, and feature-dependent spacemap behavior.
