# sources/storage-engines/wiredtiger/src/evict/evict_verbose.c

Purpose: emits human-readable cache diagnostics for eviction troubleshooting. It prints per-btree internal/leaf page counts and byte totals, then compares walked totals with tracked connection cache counters.

Important functions: `__wt_verbose_dump_cache` is the exported entry point. It prints cache-full, clean/dirty/update threshold checks, walks all eligible open btree handles under the handle-list read lock, applies cache overhead to walked bytes, and prints totals versus tracked `bytes_inmem`, dirty bytes, and update bytes. `__verbose_dump_cache_apply` iterates open handles, skipping non-btree, closed, discarded, or outdated handles. `__verbose_dump_cache_single` prints one dhandle's live/checkpoint name, eviction-disabled state, and per-page statistics gathered by a no-wait cache tree walk.

Control flow: invoked when eviction appears stuck or by diagnostic tooling. For each handle, it temporarily switches the session dhandle with `WT_WITH_DHANDLE` and walks cached pages using `WT_READ_CACHE | WT_READ_NO_EVICT | WT_READ_NO_WAIT | WT_READ_VISIBLE_ALL`. Handles opened exclusively are reported and skipped to avoid unsafe tree walking.

State and persistence behavior: this file is read-only except for message output. It observes page memory footprints, dirty state, update bytes via `__evict_page_updates_candidate`, dhandle flags, and tracked cache counters. It does not persist data or alter eviction queues.

Dependencies and integration points: depends on eviction threshold helpers from `evict_inline.h`, handle-list locking, tree walking, page dirty/update accounting, dhandle iteration macros, and WiredTiger message/verbose infrastructure. It is called from stuck-cache handling in `evict_thread.c`.

Risks and test signals: diagnostic code must not crash while the system is already unhealthy. Tests should cover exclusive handles, checkpoint handles, discarded/outdated handles, trees with no internal or no leaf pages, dirty/update byte accounting, tracked-versus-walked totals, no-wait skipped pages, and invocation while eviction threads and schema operations are active.
