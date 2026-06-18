<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/commit.go -->
# sources/storage-engines/pebble/commit.go

## Purpose
Implements Pebble's concurrent commit pipeline for writing batches to the WAL, applying them to memtables, publishing visible sequence numbers in order, and coordinating WAL sync completion.

## Important APIs, Types, and Functions
`commitQueue` is a lock-free fixed-size single-producer/multi-consumer ring of `Batch` pointers with `enqueue` and `dequeueApplied`. `commitEnv` abstracts sequence-number state and `apply`/`write` callbacks for DB integration and tests. `commitPipeline` owns queues, semaphores, and a mutex. Key methods are `newCommitPipeline`, `directWrite`, `Commit`, `AllocateSeqNum`, `prepare`, and `publish`.

## Control Flow
`Commit` reserves queue capacity, prepares the batch under `commitPipeline.mu` by enqueueing it, assigning sequence numbers, and serially writing to the WAL, then applies to the memtable concurrently. `publish` marks the batch applied, drains any applied batches from the ordered queue, ratchets `visibleSeqNum` to each drained batch's end sequence number, and releases each batch's commit wait group. If it reaches an unapplied head, it waits for another goroutine to publish it. Syncing commits add wait-group work for the WAL log writer; `noSyncWait` returns after publication and leaves fsync waiting to `Batch.SyncWait`.

## State and Persistence Behavior
The WAL write is the durable stage, while memtable application and `visibleSeqNum` publication control read visibility. `logSeqNum` is advanced atomically under the pipeline mutex; `visibleSeqNum` is ratcheted atomically in order. Fixed-capacity semaphores reserve space in the commit queue and log sync queue before taking the mutex, avoiding blocking while holding it. `AllocateSeqNum` sequences non-WAL operations such as ingestion, waits for prior writes to become visible before prepare, and publishes synthetic sequence-number allocations.

## Dependencies and Integration Points
Integrates with `Batch`, memtables, `record.LogWriter` sync queue capacity, WAL rotation, ingestion sequencing, base sequence-number visibility, and DB write options. Uses `crtime` for commit stats and runtime scheduling in spin waits.

## Risks and Edge Cases
On prepare/apply errors, comments note queue semaphore slots are not released because the batch remains in the pending queue; this makes error handling performance/capacity-sensitive and prevents batch reuse by clearing `b.db`. The ring queue relies on `record.SyncConcurrency` power-of-two sizing and external semaphores to avoid full queue. `AllocateSeqNum` spin-waits for visibility and must publish even if callbacks internally fail. `noSyncWait` allows committed data to become visible before WAL fsync completes.

## Test Signals
`commit_test.go` validates queue ordering, high-concurrency commits, sync/no-sync-wait behavior, sequence-number allocation, WAL close with full sync queues, LogData/KV sequence publication ordering, and benchmark throughput.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/commit.go -->
