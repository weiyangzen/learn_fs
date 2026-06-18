# sources/storage-engines/wiredtiger/src/btree/bt_sync_obsolete.c

## Purpose
`bt_sync_obsolete.c` implements the checkpoint-cleanup background thread. It scans eligible btrees after checkpoints, detects obsolete deleted pages and obsolete time-window metadata, marks parents dirty or pages dirty, and encourages eviction so later checkpoints can remove unneeded blocks and shrink checkpoint metadata.

## Important APIs, Types, And Functions
- `__wt_checkpoint_cleanup_create`, `__wt_checkpoint_cleanup_destroy`, and `__wt_checkpoint_cleanup_trigger` manage the server thread and condition variable.
- `__checkpoint_cleanup` is the thread body; `__checkpoint_cleanup_int` iterates eligible file URIs.
- `__checkpoint_cleanup_get_uri` scans metadata forward under read-uncommitted isolation to find the next eligible file URI.
- `__checkpoint_cleanup_eligibility` filters metadata entries using handle availability, logging, checkpoint address presence, durable timestamps, transaction visibility, write generation, history store, and tiered `.wtobj` exclusion.
- `__checkpoint_cleanup_walk_btree` opens a dhandle and walks its btree with `__wt_tree_walk_custom_skip`.
- `__checkpoint_cleanup_page_skip`, `__checkpoint_cleanup_obsolete_cleanup`, and `__sync_obsolete_cleanup_one` decide what to read and what to clean.
- `__sync_obsolete_inmem_evict_or_mark_dirty`, `__sync_obsolete_deleted_cleanup`, and `__sync_obsolete_disk_cleanup` implement page/ref-specific actions.

## Control Flow
Creation sets the checkpoint-cleanup server flag, reads configuration for cleanup method, interval, and per-file wait, opens an internal wait-capable session, allocates a condition variable, and starts the thread. The thread wakes periodically or on signal, skips work if disabled or if a disaggregated follower is not leader, and invokes the full cleanup iteration when enough time has elapsed.

The full iteration starts at `file:` and repeatedly selects the next metadata URI that is eligible. Each selected btree is opened, skipped if read-only, empty, original bulk-load, or unavailable, and walked. The custom skip callback avoids reading pages when cache pressure is high, when deleted/on-disk pages cannot produce cleanup benefit, or when non-aggressive cleanup should not reclaim logged-table space. Internal pages are traversed under a page-index generation and each child ref is inspected. Leaf pages already in memory are checked for obsolete stop times and obsolete time windows.

On-disk leaf-no-overflow pages whose stop time is globally visible are converted from disk to deleted by dirtying the parent and unlocking the ref in `WT_REF_DELETED`. Deleted refs with globally visible page-delete information dirty their parent so reconciliation can remove them. Clean in-memory pages with obsolete whole-page deletes are evicted soon; pages with overflow items are dirtied first so overflow blocks can be freed by reconciliation.

## State And Persistence Behavior
Cleanup does not directly free blocks. It changes in-memory btree/ref/page state so ordinary reconciliation and checkpoint persistence can remove obsolete references and overflow blocks safely. It increments `btree->checkpoint_cleanup_obsolete_tw_pages` and the connection-level obsolete btree counter to limit work. It may set `ref->dirty_state` for delta-enabled btrees when a disk ref becomes deleted. It marks parent pages dirty via `__wt_page_parent_modify_set`, marks page modify structures dirty via `__wt_page_modify_set`, and schedules eviction via `__wt_evict_page_soon`.

## Dependencies And Integration Points
The module integrates with metadata cursors, dhandle lookup/open/release, transaction visibility (`__wt_txn_visible_all`, `__wt_txn_has_newest_and_visible_all`), time aggregates, eviction pressure checks, the tree walker custom skip API, page-index/split generations, server flags, connection heuristic controls, logging configuration, history store URI handling, disaggregated leader state, and statistics/verbose logging.

## Risks
Eligibility and visibility mistakes can either retain too much obsolete data or dirty/delete pages too aggressively. The code intentionally uses best-effort races: ref state is checked before locking and may change, so callers must tolerate skips. Reading disk pages for cleanup can increase cache pressure; the skip callback contains several guardrails. Metadata scanning under read-uncommitted isolation must advance strictly forward to avoid looping or revisiting keys while metadata changes. Thread lifecycle must signal and join before closing the internal session.

## Test Signals
Tests should cover obsolete fast-deleted pages, pages with overflow items, obsolete time-window cleanup limits, logged-table reclaim-space mode, history store eligibility, tiered `.wtobj` exclusion, disaggregated follower skip behavior, cache-pressure skip behavior, and races with deleted/disk/memory ref transitions. Useful counters include `checkpoint_cleanup_pages_removed`, `checkpoint_cleanup_pages_evict`, `checkpoint_cleanup_pages_obsolete_tw`, `checkpoint_cleanup_pages_walk_skipped`, duration, handles processed, and success count.
