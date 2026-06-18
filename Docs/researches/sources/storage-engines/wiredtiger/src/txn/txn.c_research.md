# sources/storage-engines/wiredtiger/src/txn/txn.c Research

## Purpose
This file is WiredTiger's core transaction state machine. It manages transaction snapshots, oldest-id advancement, transaction configuration, commit/prepare/rollback, prepared-update resolution, checkpoint-cursor transaction objects, transaction statistics, session/global transaction lifecycle, shutdown checkpoint/rollback-to-stable coordination, eviction-blocking detection, and verbose diagnostics.

## Important APIs, Types, and Functions
- Snapshot and visibility: `__wt_txn_import_snapshot`, `__wt_txn_release_snapshot`, `__wt_txn_active`, `__wt_txn_get_snapshot`, `__wt_txn_bump_snapshot`, `__wt_txn_snapshot_save_and_refresh`, and `__wt_txn_snapshot_release_and_restore`.
- Oldest-id management: `__txn_oldest_scan` and `__wt_txn_update_oldest`.
- Configuration: `__wt_txn_config`, `__wt_txn_reconfigure`, and operation-timeout helpers.
- Prepared transaction internals: `__wt_txn_resolve_prepared_op`, `__txn_prepare_rollback_restore_hs_update`, `__txn_prepare_rollback_delete_key`, `__txn_resolve_prepared_update_chain`, and `__txn_mod_compare`.
- State transitions: `__wt_txn_commit`, `__wt_txn_prepare`, and `__wt_txn_rollback`.
- Lifecycle: `__wt_txn_init`, checkpoint-cursor init/close, `__wt_txn_release_resources`, `__wt_txn_destroy`, `__wt_txn_global_init`, `__wt_txn_global_destroy`, `__wt_txn_activity_drain`, and `__wt_txn_global_shutdown`.
- Diagnostics and pressure handling: `__wt_txn_stats_update`, `__wt_txn_is_blocking`, `__wt_verbose_dump_txn_one`, and `__wt_verbose_dump_txn`.

## Control Flow and State
Snapshots are built by scanning the global per-session shared transaction table under the transaction global rwlock. The code records active transaction ids into a sorted snapshot array, publishes pinned ids when requested, and uses generation tracking to avoid rebuilding valid snapshots. Oldest-id advancement performs a read scan, conditionally upgrades to a write lock, rescans to avoid races with sessions that have local snapshots not yet published, and then advances `oldest_id`, `last_running`, and `metadata_pinned` monotonically.

Commit first configures operation timeout and timestamps, releases snapshots after copying cursor values when needed, applies timestamps or resolves prepared updates, optionally enters the commit generation and checks stable timestamp movement, writes a log record under the visibility lock, then enters a no-fail region. After that point it frees transaction operations, releases the transaction id and snapshot state, advances snapshot generation for non-readonly commits, updates the global durable timestamp by CAS, validates prepared durable timestamp relative to stable, and may assist eviction.

Prepare sets prepare timestamp and prepared id, rejects logged/history/metadata updates, releases the snapshot, marks each update prepared, clears stale update pointers for normal btrees, flags repeated-key operations so commit/rollback resolves each key once, removes the transaction id from the global table, and sorts modifications by btree/key to improve resolution locality. Rollback releases the snapshot, aborts non-prepared updates, resolves prepared updates when needed, rolls back fast deletes and layered truncates, frees operations, and releases transaction state.

## State and Persistence Behavior
The file coordinates in-memory transaction ids, snapshots, pinned ids/timestamps, modification arrays, update-chain state, prepared ids, commit/durable/prepare/rollback timestamps, and global transaction timestamps. Durable effects occur through update-chain timestamp installation, history-store restoration for prepared resolution, transaction log calls, checkpoint/RTS during shutdown, and checkpoint-cursor snapshots. The commit path explicitly treats the window after logging as a corruption boundary where later failures panic.

## Dependencies and Integration Points
This module integrates with almost every storage subsystem: cursor and btree search, update chains, history store cursors, page modification and cache accounting, reconciliation-visible prepare states, logging, checkpoint, rollback-to-stable, eviction, statistics, metadata handles, session generations, operation timers, and disaggregated/layered table logic. It relies heavily on WiredTiger atomics and memory barriers to publish transaction ids and prepare-state transitions safely.

## Risks and Edge Cases
Prepared update resolution is the densest risk area. It must handle prepared updates only in memory, prepared updates restored from disk, older history-store versions, no older value, rollback tombstones, repeated keys, aborted reserve updates, and concurrent readers/reconciliation. Commit has a strict no-fail boundary after the log write. Snapshot and oldest-id code is race-sensitive around sessions allocating ids and read-uncommitted pinned ids. Shutdown logic changes behavior for disaggregated storage, precise checkpoint, stable timestamp use, panic/read-only/in-memory states, and debug checkpoint skipping. Eviction-blocking rollback policy differs between standalone and MongoDB builds.

## Test Signals
Coverage should include snapshot sorting/import/release, oldest-id advancement with active/pinned/metadata/checkpoint sessions, commit timestamp validation, non-prepared and prepared commit/rollback, repeated-key prepared transactions, prepared updates on disk with and without history-store fallback, rollback of prepared deletes with no committed value, transaction logging failure before and after no-fail boundary, shutdown rollback-to-stable plus checkpoint combinations, checkpoint cursor snapshots, eviction oldest-id rollback, and diagnostic dumps under active transactions.
