<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBufferImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBufferImpl.java

## Purpose

`SCMHADBTransactionBufferImpl` is the RocksDB-backed SCM HA transaction buffer. It batches table writes/deletes, commits latest transaction info atomically with the batch, updates snapshot position, and coordinates periodic flushing around active Ratis transaction application.

## Important APIs, Types, and Functions

Important methods are `addToBuffer`, `removeFromBuffer`, `updateLatestTrxInfo`, `getLatestTrxInfo`, snapshot getters/setters, `flush`, `flushIfNeeded`, `shouldFlush`, `init`, `beginApplyingTransaction`, `endApplyingTransaction`, `toString`, and `close`. It uses `BatchOperation`, `TransactionInfo`, `SnapshotInfo`, `SCMMetadataStore`, and `DeletedBlockLogImpl.onFlush`.

## Control Flow

Buffered writes/deletes take the read lock, increment `txFlushPending`, and append to the current batch. `updateLatestTrxInfo` rejects non-monotonic transaction info. `flush` takes the write lock and calls `flushUnderWriteLock`, which writes transaction info into the transaction table in the same batch, commits, closes the batch, updates latest snapshot, opens a new batch, notifies deleted block log flush, resets pending count, and records flush time. `flushIfNeeded` skips while applying transactions and flushes only after pending writes exceed the wait time. `init` closes any old batch and reloads transaction info from DB.

## State and Persistence Behavior

Persistent state is committed RocksDB batch contents plus `TRANSACTION_INFO_KEY`. In-memory state includes the current batch, latest transaction info, latest snapshot reference, pending flush counter, active apply counter, last snapshot time, and read/write lock.

## Dependencies and Integration Points

It integrates with `StorageContainerManager`, SCM metadata store, Ratis state machine apply and snapshots, transaction buffer monitor, checkpoint service, and deleted block log flush hooks.

## Risks and Edge Cases

`latestTrxInfo` must be updated before flush; otherwise the previous/default transaction info is committed. Active apply counters must be balanced. `flushUnderWriteLock` assumes the deleted block log is `DeletedBlockLogImpl`. `close` closes the current batch without forcing a final commit.

## Test Signals

Tests should cover add/delete batch writes, atomic transaction info commit, monotonic transaction guard, snapshot update after flush, flush-if-needed timing and active-apply suppression, init from empty and populated transaction table, deleted-block-log `onFlush`, close behavior, and concurrent read/write locking.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBufferImpl.java -->
