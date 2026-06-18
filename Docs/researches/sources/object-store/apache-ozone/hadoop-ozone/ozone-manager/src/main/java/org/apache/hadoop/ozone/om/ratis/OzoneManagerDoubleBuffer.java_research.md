# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ratis/OzoneManagerDoubleBuffer.java

## Purpose
`OzoneManagerDoubleBuffer` batches `OMClientResponse` objects from committed Ratis transactions and persists them to OM RocksDB in a background flush thread. It is the write-side persistence bridge between `OzoneManagerStateMachine.runCommand` and `OMMetadataManager` tables.

## Important APIs and Types
- `Builder` configures metadata manager, last-applied callback, tracing, maximum unflushed transaction count, thread prefix, S3 secret manager, and optional flush notifier.
- `start`, `stop`, `pause`, `unpause`, and `resume` control the daemon.
- `acquireUnFlushedTransactions` and `releaseUnFlushedTransactions` implement backpressure via a semaphore.
- `add(OMClientResponse, TermIndex)` appends to the current buffer.
- `flushTransactions`, `flushCurrentBuffer`, and `flushBatch` perform batch persistence.
- `FlushNotifier` lets callers wait until both buffers have gone through flush notifications.

## Control Flow
The state machine acquires one semaphore permit before scheduling a write. Request handling updates in-memory metadata caches and calls `doubleBuffer.add(response, termIndex)`. The daemon waits in `canFlush` until `currentBuffer` is non-empty, swaps `currentBuffer` and `readyBuffer`, splits ready entries around `CreateSnapshot` and `SnapshotPurge` barriers, and flushes each queue.

`flushBatch` sorts term indexes, adds each response to a RocksDB `BatchOperation` via `response.checkAndUpdateDB`, writes `TransactionInfo` for the last term/index, commits the batch, updates metrics, cleans metadata caches for epochs derived from each response’s `@CleanupTableInfo`, releases semaphore permits, and calls `updateLastAppliedIndex`. Snapshot barrier splitting ensures snapshot create/purge operations are isolated in standalone batches so RocksDB snapshot callbacks observe precise ordering.

## State and Persistence Behavior
The class persists OM metadata changes and the `TRANSACTION_INFO_KEY` transaction marker into RocksDB. It also cleans table caches and S3 secret cache after committed epochs. In-memory state includes two concurrent queues, daemon status flags, a pause flag, semaphore, metrics singleton, and flushed counts for testing. On unrecoverable batch errors, it calls `ExitUtils.terminate` to avoid continuing with potentially divergent DB state.

## Dependencies and Integration Points
It depends on `OMMetadataManager`, `OMClientResponse`, `BatchOperation`, `TransactionInfo`, `OMDBDefinition`, `CleanupTableInfo`, `S3SecretManager`, `TermIndex`, Hadoop `Daemon`, and tracing utilities. `OzoneManagerStateMachine` builds and owns it.

## Risks and Edge Cases
Every response class must carry `@CleanupTableInfo`; otherwise `addCleanupEntry` throws and terminates OM. Empty flush batches are not expected because `canFlush` waits for entries. `FlushNotifier` relies on a two-notification convention when both buffers are empty; tests that wait for flushes need to account for this. The semaphore must be released exactly once per flushed transaction or write application can stall. `pause` stops flushing but queued entries remain in memory.

## Test Signals
Tests should cover buffer swap behavior, snapshot/purge split barriers, transaction info persistence, cache cleanup table selection, S3 cache cleanup, semaphore backpressure, flush notifier completion, metrics updates, and fatal handling for missing cleanup annotations or RocksDB failures.
