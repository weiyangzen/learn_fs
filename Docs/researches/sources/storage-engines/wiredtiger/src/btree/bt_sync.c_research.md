# sources/storage-engines/wiredtiger/src/btree/bt_sync.c

## Purpose
`bt_sync.c` implements `__wt_sync_file`, the btree-level flushing routine used for write-leaves and checkpoint sync operations. It walks in-memory btree pages, decides which dirty pages must be reconciled, optionally schedules parallel checkpoint work, updates checkpoint progress/statistics, preserves checkpoint consistency constraints, and starts a block-manager sync after write-leaves when configured.

## Important APIs, Types, And Functions
- `__wt_sync_file(WT_SESSION_IMPL *, WT_CACHE_OP)` is the exported entry point. It handles `WT_SYNC_WRITE_LEAVES` and `WT_SYNC_CHECKPOINT`; close/discard are rejected here.
- `__sync_checkpoint_can_skip` decides whether a dirty leaf page can be skipped during checkpoint because its first dirty transaction is newer than the checkpoint snapshot and all multiblock addresses are valid.
- `__sync_dup_hazard_pointer` and `__sync_dup_walk` duplicate walk positions for checkpoint eviction experiments and parallel checkpoint workers.
- `__sync_check_for_multiblock_rec` flags disaggregated leaf pages with pending multiblock split reconciliation for eviction.
- Core types are `WT_BTREE`, `WT_REF`, `WT_PAGE`, `WT_PAGE_MODIFY`, `WT_TXN`, `WT_MULTI`, and `WT_CACHE_OP`.

## Control Flow
For `WT_SYNC_WRITE_LEAVES`, the routine exits early if the btree is not modified, takes `btree->flush_lock`, captures the oldest transaction ID, and walks cached leaf pages using `WT_READ_CACHE | WT_READ_NO_WAIT | WT_READ_SKIP_INTL`. Dirty leaves whose `update_txn` predates the captured oldest ID are reconciled with `WT_REC_CHECKPOINT`; newer hot pages are left for the full checkpoint pass.

For `WT_SYNC_CHECKPOINT`, read-committed sessions first capture a snapshot. The function takes `flush_lock`, sets `session->syncing` and the btree `syncing` state through `WAIT` to `RUNNING`, drains eviction generation, resets obsolete time-window page counters, and derives reconciliation flags. It then walks the cache with no eviction and visible-all semantics, visiting leaves and internal pages. Clean pages contribute max transaction/timestamp state and may be checked for pending multiblock reconciliation. Dirty pages are either skipped via `__sync_checkpoint_can_skip`, reconciled directly, or pushed to parallel checkpoint workers for leaf pages. Internal pages wait for parallel leaf work before evaluating dirtiness.

Cleanup releases walk references, waits for parallel checkpoint workers on error or success, releases snapshots acquired by read-committed paths, updates checkpoint generation, clears syncing state, unlocks `flush_lock`, and optionally starts an async block sync for write-leaves.

## State And Persistence Behavior
Checkpoint sync manipulates durable state indirectly through reconciliation: dirty pages become replacement blocks, multiblock results, or clean pages with persisted addresses. It also updates `btree->rec_max_txn` and `btree->rec_max_timestamp` from clean page modification metadata so later logic can decide whether the tree must remain dirty for a future checkpoint. Skipped dirty pages re-mark the tree modified because the checkpoint itself cleared the modified flag before the final pass. `btree->syncing` and `session->syncing` gate eviction/split behavior so checkpoint does not race with namespace changes or disaggregated checkpoint generation constraints.

## Dependencies And Integration Points
This file depends on tree walking (`__wt_tree_walk`, `__wt_tree_walk_custom_skip`), hazard pointers, reconciliation (`__wt_reconcile`), checkpoint parallelism (`__wt_checkpoint_parallel_*`), transaction snapshots, eviction, block-manager sync, statistics, and disaggregated-storage page metadata. It is called from checkpoint/file-sync paths while higher-level schema/checkpoint coordination is already in place. The history store and disaggregated metadata are special-cased so their dirty content is never skipped.

## Risks
The main risks are concurrency and persistence correctness: skipping an unsafe dirty page can lose checkpoint-visible data; failing to hold/release duplicated hazard pointers can leak or free active pages; clearing `btree->syncing` before updating checkpoint generation could let eviction write pages into the wrong disaggregated checkpoint. Parallel checkpoint paths require strict finish points before internal pages are reconciled. The write-leaves oldest-ID cutoff is a performance/correctness tradeoff: it avoids chasing hot updates but depends on correct `update_txn` maintenance.

## Test Signals
Useful tests include checkpoint visibility with long-running transactions, read-committed metadata checkpoints, recovery/shutdown/rollback-to-stable checkpoints where skipping must be disabled, disaggregated multiblock split checkpoints, parallel checkpoint leaf/internal ordering, and timing-stress checkpoint eviction. Statistics such as `checkpoint_pages_visited_*`, `checkpoint_pages_reconciled`, history-store reconciliation counters, and checkpoint verbose timing are operational signals.
