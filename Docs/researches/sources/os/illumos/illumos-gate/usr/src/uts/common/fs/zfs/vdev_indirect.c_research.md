# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect.c

## Role

`vdev_indirect.c` implements indirect vdevs, which represent removed vdevs. Because old block pointers in snapshots cannot all be rewritten, ZFS keeps a mapping from old offsets on the removed vdev to new locations elsewhere in the pool. This file handles that mapping at runtime, obsolete-space accounting, mapping condensation, and reconstruction of split blocks.

## Obsolete-Space Model

The file documents the full obsolete-block pipeline:
- Each indirect mapping entry can have an obsolete byte count.
- Each indirect/removing vdev can have an obsolete space map containing obsolete DVAs since the last condense.
- Each dataset can have a remap deadlist for remapped blocks still referenced by snapshots.
- The pool can have an obsolete bpobj used when snapshots are destroyed.
- Sync-time processing moves obsolete entries to per-vdev obsolete space maps.

`vdev_indirect_mark_obsolete()` adds obsolete ranges to `vdev_obsolete_segments` and dirties the vdev when the obsolete-counts feature is enabled.

`vdev_indirect_sync_obsolete()` creates the obsolete space-map object if needed, writes accumulated obsolete segments, updates feature accounting, and clears the in-core range tree.

## Condensing

Condensing reduces indirect mapping size by integrating obsolete counts and space maps, then writing a new mapping that omits fully obsolete entries.

Major flow:
- `vdev_indirect_should_condense()` decides based on obsolete percentage, obsolete space-map size, mapping size, whether another condense is active, shutdown state, and whether the vdev is fully indirect rather than still removing.
- `spa_condense_indirect_start_sync()` creates the next mapping object, records the previous obsolete space-map object, detaches the old obsolete space map from the vdev ZAP, persists `DMU_POOL_CONDENSING_INDIRECT`, creates in-core condense state, and wakes the condense thread.
- `spa_condense_indirect_thread()` reconstructs precise obsolete counts, loads the previous obsolete space map, finds resume position from the new mapping’s max offset, generates new entries, and completes via sync task unless canceled.
- `spa_condense_indirect_generate_new_mapping()` iterates old mapping entries and commits only entries not fully obsolete.
- `spa_condense_indirect_commit_entry()` queues entries per txg and schedules `spa_condense_indirect_commit_sync()`.
- `spa_condense_indirect_complete_sync()` swaps the vdev to the new mapping, frees the old mapping and previous obsolete space map, clears condense state, removes the pool-directory marker, and dirties the config.
- `spa_condense_init()`, `spa_condense_fini()`, and `spa_start_indirect_condensing_thread()` handle import/restart and thread lifecycle.

## Remapping

`vdev_indirect_remap()` is the central mapping walker:
- Starts with an old indirect range and follows mapping entries until concrete vdevs are reached.
- Handles nested indirect vdevs with an explicit stack.
- Copies adjacent mapping entries while holding `vdev_indirect_rwlock`, then drops the lock before iterating to allow condensing to proceed.
- Calls a callback for each contiguous concrete segment.
- Also calls callbacks for indirect vdevs encountered, allowing callback-specific behavior.
- Supports debug-only split reversal to exercise split-block handling.

`vdev_indirect_mapping_duplicate_adjacent_entries()` copies the mapping entries covering a requested range while the rwlock is held.

The indirect vdev ops expose this as `vdev_op_remap`.

## I/O Path

`vdev_indirect_io_start()`:
- Creates an `indirect_vsd_t` with a list of split segments.
- Uses `vdev_indirect_remap()` and `vdev_indirect_gather_splits()` to build `indirect_split_t` entries.
- For non-split blocks, issues one child zio with the original block pointer so the normal child path can verify checksums and select mirror copies.
- For split reads/writes, issues child zios per segment without per-segment block-pointer checksums.
- For scrub/resilver split reads, reads all copies from mirror children.
- Split reads that initially checksum fail are retried through full reconstruction.

`vdev_indirect_child_io_done()` aggregates child errors into the parent and releases ABD references.

## Split-Block Reconstruction

Split indirect blocks can map different byte ranges to different top-level vdevs and mirror children. Because the checksum covers the full logical block, the code may need to try combinations of segment copies.

Main pieces:
- `vdev_indirect_read_all()` reads all readable copies of all split segments, including mirror children.
- `vdev_indirect_reconstruct_io_done()` deduplicates identical child data per split, computes the number of unique combinations, and either enumerates all combinations or tries random combinations.
- `vdev_indirect_splits_checksum_validate()` assembles selected split data into the parent ABD and validates the original checksum.
- `vdev_indirect_splits_enumerate_all()` deterministically tries every unique combination when feasible.
- `vdev_indirect_splits_enumerate_randomly()` tries bounded random combinations when the search space is too large.
- `vdev_indirect_splits_damage()` is a ztest/debug helper that intentionally damages copies to validate reconstruction.
- `vdev_indirect_repair()` writes the validated good split copy back over incorrect copies and posts checksum errors.
- `vdev_indirect_all_checksum_errors()` reports checksum errors for all read children when no valid reconstruction is found.

Tunable `zfs_reconstruct_indirect_combinations_max` limits exhaustive reconstruction, and `zfs_reconstruct_indirect_damage_fraction` injects test damage.

## Ops

`vdev_indirect_open()` synthesizes size from `vdev_asize` plus label areas and preserves `vdev_ashift`.
`vdev_indirect_close()` is empty.
`vdev_indirect_ops` is a non-leaf, non-concrete vdev type with remap support and no dump I/O or xlate op.

## Risk Notes

- Indirect mapping changes are protected by `vdev_indirect_rwlock`; remap copies entries before dropping the lock to avoid holding it across recursive or callback work.
- Condensing must be restartable after import and must not include newly obsolete ranges added after the condense starts.
- Split-block reconstruction can be computationally expensive; the random bounded fallback trades completeness for bounded work.
- Repair ignores DTL guesses and writes only copies shown to differ from the reconstructed good data.
- Obsolete-space accounting is feature-gated and sync-context-sensitive.
- Mapping entry order and offset contiguity assumptions are central to remap correctness.
