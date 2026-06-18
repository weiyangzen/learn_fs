# sources/storage-engines/tikv/src/server/gc_worker/compaction_filter.rs

## Purpose

This file implements the RocksDB write-CF compaction filter used to perform MVCC GC during compaction. It decides when a compaction should run GC based on MVCC table properties, removes stale write records, deletes corresponding default-CF long values, emits tasks for bottommost MVCC deletion marks, and records detailed metrics for filtered versions, failures, rollbacks, orphan versions, and deletion cleanup.

## Important APIs, Types, And Functions

- `GcContext` is a global context for constructing write compaction filters. It stores the disk DB, store ID, shared safe point, config tracker, feature gate, GC scheduler, and region info provider.
- `GC_CONTEXT: Mutex<Option<GcContext>>` is the global handoff from GC worker initialization into RocksDB compaction filter creation.
- `CompactionFilterInitializer<EK>` provides a default no-op implementation for unsupported engines and a RocksEngine implementation that installs `GcContext`.
- `WriteCompactionFilterFactory` implements `CompactionFilterFactory` and creates `WriteCompactionFilter` only when the safe point is initialized, the DB is not stalled, config and feature gates allow it, and table properties indicate enough garbage.
- `DeleteBatch<B>` wraps either an engine write batch or a vector of keys for multi-Rocks/tablet fallback, tracking smallest/largest affected keys for ingest latch protection.
- `WriteCompactionFilter` holds safe point, engine, pending default-CF deletes, scheduled MVCC deletion marks, current MVCC key prefix, per-key state, metrics, and optional test callbacks.
- `check_need_gc` evaluates input SST MVCC properties against safe point, ratio threshold, bottommost status, version counts, deletion counts, and maximum row versions.
- `is_compaction_filter_allowed` combines config and feature gate checks; the required feature version is 5.0.0 unless version checking is skipped.

## Control Flow

Filter factory creation locks `GC_CONTEXT`, reads the current safe point and config, rejects uninitialized or disallowed states, drops the lock, then checks input table properties. When a filter is created, RocksDB calls `featured_filter` for write-CF keys. `do_filter` splits the timestamp from the key, ignores versions newer than the safe point and non-value entries, switches per-user-key state when the MVCC key prefix changes, parses the write record, and removes rollback/lock records plus older records after the first retained Put/Delete before the safe point. For long Put values, `handle_filtered_write` schedules the default-CF payload delete. When a bottommost Delete write becomes the retained version and no older overlapping records remain, the filter queues the user key for `GcTask::GcKeys`.

Pending default-CF deletes are flushed in bounded batches with `WriteOptions::set_no_slowdown(true)` and an ingest latch over the affected key range. If inline flushing fails or the fallback vector path is used, the filter constructs `GcTask::OrphanVersions` so the GC worker can clean those default-CF versions later. On drop, the filter finalizes pending deletion marks, flushes pending writes, syncs WAL when it has a Rocks engine, and flushes local metrics.

## State And Persistence Behavior

The safe point is read from an `Arc<AtomicU64>` and is fixed per filter instance. Filter progress is in-memory and per-compaction. Persistence changes happen through delete write batches against default CF, scheduled GC tasks, and WAL sync after filter drop. `OrphanVersions` exists because a compaction result may be installed before default-CF cleanup finishes; the file explicitly notes a crash window where orphan versions can remain until a future default compaction filter exists.

## Dependencies And Integration Points

The file integrates RocksDB raw compaction filter APIs, MVCC table property decoding, TiKV transaction key and write parsing, the GC worker scheduler, region info lookup for later key cleanup, feature gating from PD, file-system IO type tagging, failpoints, and Prometheus metrics. It is initialized by `GcWorker::start_auto_gc` and consumed by RocksDB write-CF compactions.

## Risks

- `GC_CONTEXT` is global mutable process state; tests and multiple engine modes must clear or replace it carefully.
- Compaction filter correctness depends on write-CF ordering and timestamp parsing; malformed keys or values disable filtering after logging a failure.
- The orphan-version crash window can leave default-CF garbage.
- Inline delete flush uses no-slowdown and can fail under pressure, shifting load to async GC worker tasks.
- Bottommost deletion handling must not expose older versions; it only schedules deletion-mark cleanup when overlap tracking proves older records were removed.
- Ratio-threshold behavior can disable GC for negative or infinite values and force GC for values below 1.0.

## Test Signals

Tests cover feature-gate behavior, basic MVCC GC safety, deletion-mark handling across repeated compactions, MVCC property thresholds and bottommost behavior, `RemoveAndSkipUntil` safety across internal and bottommost levels, and `DeleteBatch` smallest/largest tracking. Failpoints cover write-batch flush failures, latch acquisition, filter entry, and test hooks for compaction execution.
