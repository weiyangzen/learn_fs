# sources/storage-engines/wiredtiger/src/rollback_to_stable/rts_history.c

Purpose: contains history-store cleanup operations used by rollback-to-stable, including key-range deletion, whole-btree truncation, and the final pass that rolls back the history store itself.

Important APIs and functions: `__wti_rts_history_delete_hs` deletes history-store records for the current btree/key until it reaches a stable stop timestamp. `__wti_rts_history_btree_hs_truncate` truncates all history-store records for a btree id. `__wti_rts_history_final_pass` evaluates history-store checkpoint metadata and invokes the normal btree rollback walk on the history-store file when required.

Control flow: key deletion opens a history-store cursor for `S2BT(session)->id`, reads all committed history records for the key from newest backwards via `__wt_curhs_search_near_before`, and removes records whose stop timestamp is greater than the stable data-store timestamp. Whole-btree truncation delegates to `__wt_hs_btree_truncate` unless RTS is in dry-run mode. The final pass loads `WT_HS_URI` metadata, scans checkpoint entries for newest stop durable and newest stop timestamps, opens the history-store dhandle, and calls `__wti_rts_btree_walk_btree` if the history store is dirty or newer than the rollback timestamp. Partial backup restore additionally truncates ids listed in `backup.partial_remove_ids`.

State and persistence behavior: the file removes rows from the history store and increments RTS/history-store stats. Dry-run mode preserves records while still accounting. Final-pass processing can mutate the history-store btree through the same page rollback machinery used for data files. Metadata strings and dhandles are opened and released locally.

Dependencies and integration points: depends on history-store cursor APIs, metadata search/config parsing, `rts_btree_walk.c` for btree walking, connection backup partial-restore state, and RTS stats/verbose tags. It is called from `rts_btree.c` when a stable data-store update requires trimming newer history records and from top-level RTS sequencing for history-store cleanup.

Risks: deletion boundaries are timestamp-sensitive: stopping too early leaves unstable history, while deleting too far can remove versions needed for stable reads. The final pass uses history-store-specific max timestamp calculation because prepared updates can have unusual stop metadata. Best-effort truncation during partial restore must not hide serious corruption in normal operation.

Test signals: cover history-store key deletion around exact stable timestamps, globally visible starts, dry-run behavior, non-timestamped btree truncation, history-store final pass with dirty and clean metadata, prepared history records, and partial backup restore remove-id truncation.
