# sources/storage-engines/wiredtiger/src/txn/txn_log.c Research

## Purpose
This file handles transaction log record construction, commit log writes, checkpoint/file-sync log records, truncate logging, transaction operation cleanup, timestamp log operations, and human-readable printlog output.

## Important APIs, Types, and Functions
- Operation logging helpers: `__txn_op_log_row_key_check`, `__txn_op_log`, `__txn_logrec_init`, and public `__wt_txn_log_op`.
- Commit logging: `__wti_txn_log_commit`.
- Checkpoint/file sync: `__txn_log_file_sync`, `__wti_txn_checkpoint_logread`, and `__wt_checkpoint_log`.
- Timestamp logging: `__wti_txn_ts_log`.
- Truncate logging: `__wt_txn_truncate_log` and `__wt_txn_truncate_end`.
- Cleanup and printing: `__wt_txn_op_free`, `__txn_oplist_printlog`, `__txn_printlog`, and public `__wt_txn_printlog`.

## Control Flow and State
`__wt_txn_log_op` operates on the last transaction modification and appends the appropriate packed operation to the transaction's in-memory log record. Row-store operations pack keys and values/removes; column-store operations pack recnos. Modify operations are logged as modify records only when idempotent; size-changing non-idempotent modifies are logged as full puts to keep recovery safe. `__txn_logrec_init` lazily allocates the commit log record header and transaction id. Commit simply writes the accumulated log record with the transaction's sync flags.

Checkpoint logging is multi-stage. Prepare marks a full checkpoint, writes a checkpoint-start system/message record depending on log version, briefly takes the visibility write lock to ensure logged transactions are visible, and force-syncs the checkpoint LSN. Start copies the transaction snapshot into packed scratch space. Stop writes the checkpoint record containing the checkpoint LSN and snapshot, optionally updates the logging subsystem checkpoint LSN for log removal, and falls through to cleanup. File-sync checkpoint logging uses a separate `WT_LOGREC_FILE_SYNC` record unless a full checkpoint is already in progress.

## State and Persistence Behavior
This is a persistence-critical module. It determines the exact logical operations recovery replays, the transaction id associated with commit records, timestamp records used by recovery/debugging, checkpoint LSN records used to bound recovery, and truncate range records. It also frees transaction operation memory and decrements dhandle in-use counts, which affects handle lifetime after transaction completion.

## Dependencies and Integration Points
The file integrates with log packing/unpacking generated helpers, the log manager, btree/cursor state, transaction modification arrays, truncate metadata, checkpoint transaction state, visibility locks in `txn_global`, filesystem stream output, and recovery printlog infrastructure. It is called by cursor update paths, truncate paths, transaction commit, timestamp setting, checkpoint, and user-facing log printing.

## Risks and Edge Cases
Recovery idempotence is the key risk: non-idempotent modifies must be logged as full values. Row-key diagnostic checking compares the cursor key with the page/insert key and can fail hard under diagnostic validation. Truncate logging preserves original explicit cursor keys rather than potentially changed local bounds. Checkpoint cleanup must release scratch snapshot buffers on every path. Visibility lock ordering around checkpoint prepare and commit logging is essential so checkpoint LSNs reflect visible data. `__wt_txn_op_free` can be called more than once on `WT_TXN_OP_NONE`, but other operation types require correct dhandle reference balancing.

## Test Signals
Tests should cover row/column put/modify/remove logging, non-idempotent modify recovery as full put, diagnostic row-key mismatch detection, logged truncate ranges with explicit start/stop combinations, sync flag inheritance and commit-time overrides, checkpoint prepare/start/stop/cleanup sequences for old and new log versions, hot-backup and dirty-recovery conditions that suppress log removal, timestamp log records for prepared and non-prepared transactions, printlog JSON/message output, and operation free idempotence for cleared ops.
