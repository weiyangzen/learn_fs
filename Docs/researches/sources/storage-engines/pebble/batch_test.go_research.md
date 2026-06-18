# sources/storage-engines/pebble/batch_test.go

## Purpose
`batch_test.go` is the primary behavioral regression suite for Pebble batches. It validates the binary record stream, deferred APIs, indexed-batch semantics, flushable-batch behavior, range-key/range-delete span handling, lifecycle reuse, commit statistics, and selected performance benchmarks.

## Important APIs, Types, And Functions
The file defines many `Test*` functions, with notable coverage in `TestBatch`, `TestBatchIngestSSTWithBlobs`, `TestBatchApplyPropagatesMinimumFormatMajorVersion`, `TestBatchReset`, `TestBatchReuse`, `TestIndexedBatchReset`, `TestIndexedBatchMutation`, `TestBatchIterStrictPrefix`, `TestBatchRangeOps`, `TestFlushableBatchIterStrictPrefix`, `TestFlushableBatch`, `TestBatchCommitStats`, `TestBatchLogDataMemtableSize`, `TestBatchSpanCaching`, and `TestBatchOption`. Benchmarks compare normal and indexed `Set` paths and deferred variants.

## Control Flow
Tests create in-memory DBs, raw `Batch` instances, or indexed batches, apply operations through public, deferred, and `AddInternalKey` APIs, then inspect `Reader` output, iterators, counts, memtable sizes, and internal fields. Datadriven tests parse commands such as `define`, `apply`, `iter`, `scan`, `clone`, `mutate`, and `dump`, letting golden files exercise many iterator states. Some tests deliberately manipulate internal wait groups, format versions, batch sequence numbers, lifecycle refs, and `data` capacity to hit non-public states.

## State And Persistence Behavior
The tests verify that record counts and serialized headers are consistent; that `LogData` affects WAL representation but not memtable size/count; that ingest batches remain WAL-only and may encode blob IDs; that `Reset` clears commit and range-cache state while preserving reusable configuration; and that `ApplyNoSyncWait` makes keys visible before fsync completion while `SyncWait` observes durability errors. Flushable tests confirm sequence-number assignment, sorted point offsets, and range span output for large-batch commit behavior.

## Dependencies And Integration Points
The suite uses `datadriven`, `leaktest`, `testutils`, `testkeys`, `itertest`, `batchrepr`, `batchskl`, `keyspan`, and in-memory `vfs`. It integrates with broader Pebble helpers such as `runBatchDefineCmd`, `runIterCmd`, iterator cloning, DB flush/commit paths, and Cockroach-style key comparers.

## Risks And Edge Cases
The tests target risks around empty keys/values, zero-length batches, count overflow, oversized batches, stale indexed iterators after mutation, prefix mode crossing prefix boundaries, snapshot filtering within batch sequence numbers, range span cache staleness after writes, lifecycle-close double use, and false failures from timing-sensitive commit-stat assertions. Randomized span caching logs a seed because failures may be order-dependent.

## Test Signals
This file itself is the signal source. It combines table tests, datadriven golden tests, direct internal-state assertions, benchmarks, and randomized stress. Important missing areas are mostly external: real filesystem WAL failover races and production-scale >4 GiB behavior are represented by guards or unit-level simulation rather than full end-to-end tests.
