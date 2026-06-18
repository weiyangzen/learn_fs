# sources/storage-engines/wiredtiger/src/evict/evict_file.c

Purpose: performs whole-file/tree eviction for close and discard operations. It walks every cached page in a btree under exclusive eviction access and either reconciles dirty content for close or discards pages directly for discard.

Important API: `__wt_evict_file(WT_SESSION_IMPL *session, WT_CACHE_OP syncop)` supports `WT_SYNC_CLOSE` and `WT_SYNC_DISCARD`. For close, dirty pages are reconciled with `WT_REC_EVICT`, `WT_REC_EVICT_CALL_CLOSING`, `WT_REC_CLEAN_AFTER_REC`, `WT_REC_VISIBLE_NO_SNAPSHOT`, and usually `WT_REC_HS` unless the file is history store, metadata, or disaggregated metadata. For discard, it validates that pages are safe to lose and calls `__wt_ref_out` without reconciliation.

Control flow: the function asserts `evict_disabled > 0` or the handle is no longer open, exits early when the root has no page, updates the oldest transaction ID, and handles a disaggregated discard guard via `__wt_btree_can_discard`. It walks with `WT_READ_CACHE | WT_READ_NO_EVICT` and uses `WT_READ_VISIBLE_ALL` when the session has no snapshot. Each returned page is reconciled before advancing the walk because reconciliation can reshape the tree; then the previous ref is evicted or discarded.

State and persistence behavior: for `WT_SYNC_CLOSE`, dirty pages are written/reconciled before `__wt_evict` updates refs and frees in-memory pages, preserving durability and history-store requirements. For `WT_SYNC_DISCARD`, both clean and dirty in-memory images can be discarded, so disaggregated checks prevent losing pages that cannot be retrieved later. The function clears any outstanding tree-walk reference on error.

Dependencies and integration points: depends on exclusive eviction from `evict_exclusive.c`, tree walking, transaction oldest updates, reconciliation, page eviction, disaggregated materialization checks, and close/discard callers in btree/schema lifecycle code.

Risks and test signals: the ordering of reconcile-before-next-walk prevents missing pages after tree shape changes. Tests should cover close of dirty trees, empty trees, instantiated/deleted pages, disaggregated discard when pages cannot be discarded, checkpoint snapshot/no-snapshot sessions, `WT_SYNC_DISCARD` during connection closing, and error cleanup when reconciliation or eviction returns `EBUSY`.
