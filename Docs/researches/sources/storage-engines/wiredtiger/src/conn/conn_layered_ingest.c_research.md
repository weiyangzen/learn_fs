# sources/storage-engines/wiredtiger/src/conn/conn_layered_ingest.c

## Purpose
This file drains disaggregated layered ingest tables into stable tables, replays follower-recorded truncates in timestamp order, handles prepared-update edge cases during step-up, clears ingest tables after drain, and advances ingest-table prune timestamps for garbage collection after checkpoints.

## Important APIs, Types, and Functions
`__wti_layered_drain_ingest_tables` is the step-up entry point. It initializes `conn->layered_drain_data.work_queue`, starts optional drain worker threads, queues open ingest dhandles, uses the caller thread as a worker, stops the thread group, and clears remaining work.

`__layered_copy_ingest_table` is the core data movement routine. It derives the stable URI from an ingest URI, opens the stable table with overwrite, opens a version cursor on the ingest table with raw key/value and timestamp-order dump options, builds update chains for each key whose durable timestamp falls in a requested range, fixes or resolves prepared transactions when needed, and applies updates to stable via `__layered_move_updates`.

`__layered_drain_ingest_table_and_truncate_list` derives the parent layered URI, obtains committed truncates from `WT_LAYERED_TABLE.truncateqh`, sorts them by start timestamp with `__truncate_cmp_by_start_ts`, copies ingest updates between truncate timestamps, replays each truncate with `__layered_apply_truncate_to_stable`, and then copies the remaining updates through `WT_TS_MAX`.

Prepared-update helpers include `__layered_assert_stable_btree_state`, `__layered_fix_prepared_transaction_callback`, and `__layered_fix_prepared_transaction`. GC helpers include `__layered_update_ingest_table_prune_timestamp`, `__wti_layered_iterate_ingest_tables_for_gc_pruning`, and `__layered_last_checkpoint_order`.

## Control Flow and Behavior
Step-up drain scans the connection's open dhandle list under the handle-list read lock and queues open btree handles whose URI is an ingest table. Each queued dhandle is pinned via `session_inuse`; the worker decrements that pin when done. If `drain_threads > 1`, a thread group runs workers in parallel while the initiating thread also drains work items until the queue is empty.

For each ingest table, the worker copies ingest data to the stable table interleaved with committed truncates, truncates the ingest table in its own timestamp-free transaction, optionally verifies it is empty in diagnostic builds, and resets its prune timestamp to `WT_TS_NONE` so dirty ingest pages can be evicted immediately after step-up.

The copy routine uses a version cursor that can skip updates at or below the later of `from_ts` and the last checkpoint timestamp. Prepared updates are included only on the final pass to `WT_TS_MAX`. For each key, it accumulates a linked list of `WT_UPDATE` objects representing standard values, tombstones, unresolved prepared updates, resolved prepared updates, or aborted prepared updates. Before applying the chain, it searches the stable btree and asserts stable-side invariants: no unresolved preserved prepared update remains unless it is being resolved, and tombstones have a value to delete unless globally visible.

When preserve-prepared is enabled, the code either resolves previously checkpointed prepared cells on stable or patches in-flight prepared transaction operations so later commit/rollback refers to the stable btree instead of the ingest btree. Follower-recorded fast truncates are replayed against stable with `WT_SESSION_INGEST_REPLAY` and the original transaction id, commit timestamp, and durable timestamp.

After checkpoints, pruning walks the layered table manager entries. For each layered table it computes which stable checkpoints are still in use by checkpoint dhandles, derives a safe prune timestamp, opens the ingest btree if available, and monotonically advances `btree->prune_timestamp`.

## State and Persistence Behavior
Draining persists ingest updates into stable tables by modifying stable btrees. It then clears ingest contents with truncate. The operation is part of role transition rather than a user transaction stream; it assumes no competing transactions except the prepared transaction repair cases explicitly handled.

The work queue and thread state are in-memory and destroyed after drain. Truncate entries live on the layered table and are cleared after replay. Prepared transaction repair mutates in-memory transaction operation arrays and dhandle `session_inuse` counts so later transaction resolution remains balanced. Prune timestamps are in-memory btree fields used by eviction/GC to decide which ingest content can be removed.

## Dependencies and Integration Points
This file integrates with layered cursor/truncate code, transaction prepared-state machinery, version cursors, btree row search/modify, schema open/truncate APIs, dhandle reference accounting, layered table manager entries, checkpoint metadata, and disaggregated role step-up in `conn_layered.c`.

It is closely tied to `WT_CONN_PRESERVE_PREPARED`, timestamp rules, disaggregated stable/ingest URI naming (`.wt_stable`, `.wt_ingest`), and checkpoint pickup finalization, which calls `__wti_layered_iterate_ingest_tables_for_gc_pruning`.

## Risks
This is a high-risk data movement path. Timestamp range partitioning must be correct so updates before each truncate are copied before replaying that truncate and later updates are copied afterward. Prepared transaction handling is explicitly temporary and assumes no concurrent commit/rollback and no prepared fast-truncate operations.

The stable btree assertions protect against illegal delta chains, unresolved prepared cells, and tombstones without values. If step-down/step-up carries stale btree pages across roles, drain can encounter prepared state that reconciliation cannot represent. Worker parallelism depends on pinning dhandles correctly and clearing the queue on errors without leaks.

Prune timestamp computation depends on checkpoint handle naming and reference counts. If it advances too far, needed ingest history can be pruned while a checkpoint cursor still needs it; if it does not advance, ingest garbage accumulates.

## Test Signals
Signals include layered step-up tests, layered prepare tests, layered fast-truncate tests, disaggregated format configurations with variable `disagg.drain_threads`, and model failover tests that pick up checkpoints then reconfigure to leader. Diagnostic assertions check empty ingest tables and stable btree prepared/tombstone invariants. Useful runtime checks are successful step-up, no leaked dhandle references, stable table contents matching ingest history plus truncates, correct commit/rollback of prepared transactions after drain, and monotonic ingest prune timestamps.
