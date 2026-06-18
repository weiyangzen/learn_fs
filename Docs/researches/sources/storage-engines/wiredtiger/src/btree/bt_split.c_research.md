# sources/storage-engines/wiredtiger/src/btree/bt_split.c

## Purpose

`bt_split.c` implements WiredTiger's btree split machinery for reconciled pages, in-memory insert splits, internal page splits, root deepening, reverse splits, and one-for-one page rewrites. It is responsible for live topology changes while concurrent readers, eviction, reconciliation, checkpoint, and update restoration may be active. The complete 2573-line source was read.

## Important APIs, Types, and Functions

Exported entry points are `__wt_split_insert`, `__wt_split_multi`, `__wt_split_reverse`, `__wt_split_rewrite`, and `__wt_multi_to_ref`. Central helpers include `__split_parent`, `__split_root`, `__split_internal`, `__split_parent_climb`, `__split_internal_lock`, `__split_ref_move`, `__split_ref_prepare`, `__split_ref_final`, `__split_multi_inmem`, `__split_multi_inmem_final`, and `__split_multi_inmem_fail`. `WT_SPLIT_ERROR_PHASE` defines whether errors are returnable, fatal, or ignorable after publication.

## Control Flow

Split paths allocate all new refs/pages/indexes first, switch to fatal error mode before publishing tree changes, swap page indexes to make the split visible, record split generations, safely free old structures after readers drain, update memory accounting, and advance `WT_GEN_SPLIT`.

`__split_parent` rewrites a parent index, optionally removes globally deleted child refs, publishes replacement refs, marks dirty internal state, converts discarded refs to `WT_REF_SPLIT`, stashes old indexes, and handles empty-parent `EBUSY`. `__split_root` deepens the tree by chunking root refs into new internal children. `__split_internal` right-splits non-root internal pages. `__split_multi` converts reconciliation `WT_MULTI` outputs to refs, installs them, finalizes update movement, and discards the original page. `__split_insert` moves the last insert-list item to a new right page. `__wt_split_rewrite` rebuilds a problematic page in place using the multi-inmem restoration path.

## State and Persistence Behavior

The file mutates live in-memory btree topology and carries persistent disk addresses from reconciliation into new `WT_REF` objects. It consumes disk images to instantiate pages, restores unresolved update chains, updates dirty/checkpoint state, and maintains page memory footprints. Split generations and deferred frees protect old page indexes and refs still visible to readers. Replaced refs are marked `WT_REF_SPLIT` so readers restart through the new parent index.

## Dependencies and Integration Points

It integrates with reconciliation (`WT_MULTI`, `WT_SAVE_UPD`), eviction, page allocation, row/column search and modify, update chains, prepared transaction preservation, overflow discard, cache accounting, page-index generation protection, checkpoints, prefetch, internal delta state, disaggregated materialization checks, timing stress hooks, and diagnostic key-order verification.

## Risks and Edge Cases

This file is concurrency-critical. After an index swap, rollback is impossible because readers may use the new structure. Memory lifetime is delicate for old indexes, moved refs, on-page keys/addresses, and prefetch-queued refs. Internal splits are avoided during sync/checkpoint to prevent traversal holes. Update restoration must retain enough prepared and older updates for rollback and future reconciliation. Overflow internal keys must be discarded exactly once. VLCS leftmost deleted refs and prefetch flags require special handling during parent cleanup.

## Test Signals

Cover eviction multi-block splits, row/VLCS insert splits, reverse splits, root deepening, internal split climbing, failures before and after publication, concurrent readers on old indexes, checkpoint plus insert split, sync suppression of internal splits, deleted-child cleanup, prefetch-protected refs, overflow internal keys, prepared/modify update restoration, disaggregated materialization, and `WT_TIMING_STRESS_SPLIT_*` plus eviction split failpoints.
