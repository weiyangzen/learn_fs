# sources/storage-engines/wiredtiger/src/evict/evict_walk.c

## Purpose
This file implements the eviction server's tree walk logic. Its job is to choose a btree handle, traverse pages from a remembered or randomized point, score pages, and place ordinary or urgent candidates on eviction queues. It is the bridge between global cache pressure signals and per-page eviction decisions.

## Important APIs, Types, And Functions
The exported entry point is `__wti_evict_walk`, which fills a `WTI_EVICT_QUEUE` by selecting handles from the connection dhandle list and calling `__evict_walk_tree`. `__wti_evict_push_candidate` atomically marks a `WT_PAGE` with `WT_PAGE_EVICT_LRU`, initializes the queue entry, and computes its score through `__evict_entry_priority`. Exclusive-eviction paths use `__wti_evict_clear_all_walks_and_saved_tree` and `__wti_evict_clear_walk_and_saved_tree_if_current_locked` to drop pinned walk points. The main internal helpers are `__evict_walk_choose_dhandle`, `__evict_btree_dominating_cache`, `__evict_walk_target`, `__evict_get_target_pages`, `__evict_walk_prepare`, `__evict_try_restore_walk_position`, `__evict_should_give_up_walk`, `__evict_skip_dirty_candidate`, and `__evict_try_queue_page`.

## Control Flow
`__wti_evict_walk` determines how many queue slots to fill, caps the work to avoid monopolizing all candidates, then loops over dhandles while holding and releasing `dhandle_lock` around handle selection. It skips closed, non-btree, eviction-disabled, readonly, checkpointing, disaggregated checkpointed, sticky, inactive, or in-memory clean-only handles. Once a handle is chosen, it stores it as the saved walk tree, releases the dhandle list lock, obtains `evict_walk_lock`, and calls `__evict_walk_tree`.

`__evict_walk_tree` computes the target number of pages for the tree from clean, dirty, and update bytes. It prepares the starting ref using an existing hard pointer, a soft normalized position, the root, or a random descent. It then walks refs using `__wt_tree_walk_count`, updates visit statistics, skips roots and already queued pages, and asks `__evict_try_queue_page` whether each page matches the current eviction mode. It stops after enough candidates, two end-of-tree restarts, or a poor candidate-to-page ratio.

## State And Persistence Behavior
The key persistent-in-memory state is stored on `WT_BTREE`: `evict_ref`, `evict_pos`, `evict_saved_ref_check`, `evict_start_type`, `evict_walk_target`, `evict_walk_progress`, `evict_walk_period`, `evict_walk_skips`, `last_evict_walk_flags`, and `evict_priority`. Pages are not written here, but this file selects dirty pages whose later eviction may reconcile pages and update disk/history-store state. When normalized positions are enabled, `__evict_clear_walk` converts a held ref into a soft tree position and releases the hazard pointer so exclusive file operations can proceed.

## Dependencies And Integration Points
The file depends heavily on `btree.h` normalized positions and eviction walk types, `btmem.h` read flags, page/ref states, read generations, modification metadata, and update-candidate helpers. It integrates with the eviction subsystem through `WT_EVICT`, `WTI_EVICT_QUEUE`, urgent queueing, cache pressure flags, and connection statistics. It coordinates with transaction visibility through snapshots and `last_running`, with checkpoint state through `WT_BTREE_SYNCING` and precise checkpoint checks, and with disaggregated storage through garbage-collect btrees, stable checkpointed trees, prune timestamps, HS-dirty prioritization, and page-delta LSN state.

## Risks
The main correctness risks are stale walk refs, leaked hazard pointers, queueing the same page twice, evicting pages whose updates are not visible enough to reconcile, starving trees because `evict_walk_period` grows too aggressively, and bad interactions with checkpoints or disaggregated trees. The soft-position path is sensitive to tree splits because a restored position may not identify the original ref. The dirty-page skip heuristics are workload-sensitive: too strict can starve eviction, too loose can thrash reconciliation and history-store growth.

## Test Signals
Useful signals include eviction statistics for skipped trees/pages, walk give-up reasons, restored-position counters, ordinary and urgent queued pages, internal-page queue counts, dirty/update pressure tests, checkpoint plus eviction concurrency, exclusive file close while eviction walks are active, in-memory btree behavior, disaggregated checkpoint follower/leader cases, history-store dirty pressure, and stress tests with many handles and split-heavy trees.
