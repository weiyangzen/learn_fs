<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/commit_test.go -->
# sources/storage-engines/pebble/commit_test.go

## Purpose
Tests and benchmarks Pebble's commit queue and commit pipeline concurrency, sync, sequencing, and WAL-close behavior.

## Important APIs, Types, and Functions
`testCommitEnv` supplies `commitEnv` callbacks with atomic sequence numbers, write counts, apply buffers, and optional sync-queue blocking. `TestCommitQueue`, `TestCommitPipeline`, `TestCommitPipelineSync`, `TestCommitPipelineAllocateSeqNum`, `syncDelayFile`, `TestCommitPipelineWALClose`, `TestCommitPipelineLogDataSeqNum`, and `BenchmarkCommitPipeline` cover functionality and performance.

## Control Flow
Queue tests enqueue batches, mark them applied out of order, and verify only the head drains. Pipeline tests launch thousands of goroutines committing one-key batches, then verify write/apply counts and sequence numbers. Sync tests exercise both synchronous wait and `noSyncWait` plus `Batch.SyncWait`. WAL close tests fill commit concurrency with sync-blocked WAL records, unblock sync, close the WAL, and assert no queue-full panic. The LogData test commits a KV and zero-count log data concurrently and asserts `visibleSeqNum` never makes the KV visible before apply returns.

## State and Persistence Behavior
Most tests use fake commit environments in memory. WAL-close and benchmark paths use `record.LogWriter`; `syncDelayFile` controls fsync completion. The benchmark writes to `io.Discard` while applying to an in-memory memtable and exercising real log writer sync queue behavior.

## Dependencies and Integration Points
Depends on batches, base sequence numbers, memtables, arena skiplist errors, record log writer, VFS, race/build tags, and testify/require. It tests the commit pipeline in isolation rather than through full DB writes.

## Risks and Edge Cases
High goroutine counts are reduced under race/slow builds. Fake environments may not cover all DB-level callback failures. Some tests rely on timing/jitter to exercise interleavings, especially LogData sequencing. Benchmarks allocate batches and random keys in timed loops.

## Test Signals
Signals include exact final `logSeqNum` and `visibleSeqNum`, all batches applied/written, successful async sync waits, nonzero sequence allocation behavior, clean WAL close under full sync queue pressure, and no premature KV visibility during concurrent LogData commit.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/commit_test.go -->
