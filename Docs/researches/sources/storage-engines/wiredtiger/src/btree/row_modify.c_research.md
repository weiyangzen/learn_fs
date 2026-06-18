# sources/storage-engines/wiredtiger/src/btree/row_modify.c

## Purpose
`row_modify.c` implements row-store page modification and update-chain cleanup. It allocates page modify structures, inserts or updates row-store `WT_INSERT` skiplists and `WT_UPDATE` chains, logs cursor-originated transaction operations, and scans long update chains for obsolete globally visible suffixes that can be freed or should trigger forced eviction.

## Important APIs, Types, And Functions
- `__wt_page_modify_alloc` allocates and atomically installs `WT_PAGE_MODIFY`.
- `__wt_row_modify` is the row-store insert/update/delete/reserve/tombstone entry point.
- `__wt_update_obsolete_check` truncates obsolete update chains and schedules eviction for very long chains.
- `__row_insert_alloc` creates row-keyed `WT_INSERT` nodes.
- Major collaborators are `__wt_update_serial`, `__wt_insert_serial`, `__wt_txn_modify_check`, `__wt_txn_modify`, `__wt_txn_log_op`, `__wt_txn_op_set_key`, and `__wt_free_obsolete_updates`.

## Control Flow
`__wt_page_modify_alloc` initializes the page modification spinlock and installs the modify structure with CAS, charging page memory only for the winner.

`__wt_row_modify` validates its input mode, ensures a modify structure, then branches on `cbt->compare`. For exact matches, it targets either the on-page update array slot or the existing insert's update pointer. Cursor-originated writes check conflicts, allocate a new update, assign a transaction ID, and save the value into `cbt->modify_update`. Internal restore paths measure and prepend an existing update list, with special assertions for history-store and prepared/disaggregated cases. The new update is linked to the old chain and serialized into place.

For inserts, the code allocates the row insert-head array with an extra smallest-key slot, chooses the slot from `WT_CBT_SEARCH_SMALLEST` or the search slot, optionally runs diagnostic lower-bound checks against the parent separator, allocates the insert head, skiplist node, and update, initializes skiplist next pointers from the search stack, and serializes insertion.

After linking, cursor-originated non-reserve writes are logged and the key is copied into transaction operation state. Error cleanup frees only objects that have not been inserted into page memory; linked updates are left for rollback.

`__wt_update_obsolete_check` try-locks the page, scans an update chain for a globally visible data update after which older updates can be freed, avoids truncating chains requiring history-store cleanup, schedules eviction if the chain exceeds 1000 updates, and records transaction/timestamp state to avoid repeated scans of long chains.

## State And Persistence Behavior
This file mutates in-memory row modification state and transaction state. Durable effects occur later through write-ahead logging and reconciliation. Page memory accounting is updated for modify allocation and serialized insert/update functions. Transaction modify/log state ensures rollback, prepare, and recovery can find the corresponding key/update. Obsolete update removal changes in-memory chains only when a globally visible value safely terminates history needed by readers.

## Dependencies And Integration Points
Row modify depends on row search state (`compare`, `slot`, `ins`, search stacks, `WT_CBT_SEARCH_SMALLEST`), transaction conflict/visibility machinery, history-store special rules, prepared update preservation, disaggregated restore behavior, skiplist serialization, page locks, cache accounting, and eviction scheduling. It is a high-traffic path for `WT_CURSOR.insert/update/remove/reserve` on row-store tables.

## Risks
Ownership after partial failure is the major risk: after an update is linked into page memory, local cleanup must not free it. The smallest-key insert slot can corrupt tree ordering if used on a non-leftmost child with a key below the parent separator, hence the diagnostic check. Restore paths have strict assumptions about existing update chains. Obsolete-chain truncation must not discard updates needed for history-store deletion or active readers, and long chains can cause performance regressions if eviction is not triggered.

## Test Signals
Tests should cover on-page updates, insert-list updates, new inserts before first key and between keys, smallest-slot lower-bound diagnostics, tombstone/reserve operations, internal update-list restoration, history-store-specific assertions, prepared update preservation, transaction log/key recording failure after linking, rollback cleanup, obsolete update truncation, long-chain forced eviction, and concurrent modify allocation races.
