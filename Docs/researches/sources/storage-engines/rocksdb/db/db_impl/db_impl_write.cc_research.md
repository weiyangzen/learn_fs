# sources/storage-engines/rocksdb/db/db_impl/db_impl_write.cc

## sources/storage-engines/rocksdb/db/db_impl/db_impl_write.cc

### Purpose

`db_impl_write.cc` is RocksDB's central DB write-path implementation. It turns public `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, `DeleteRange`, `Write`, `WriteWithCallback`, and `IngestWriteBatchWithIndex` calls into ordered WAL records, sequence-number assignment, memtable inserts, optional blob direct writes, write throttling/stalling, WAL switching, flush scheduling, recoverable transaction-state publication, and convenience default `DB` method implementations.

### Important APIs, Types, And Functions

- Public and DBImpl convenience methods validate timestamp compatibility and construct `WriteBatch` wrappers for single-key operations.
- `BlobWriteRollbackGuard` rolls back blob direct-write garbage accounting unless the write completes successfully.
- `PutEntityFastPathWriteCallback` disables batching for deferred `PutEntity` materialization.
- `BlobDirectWriteContext` caches per-CF referenced SuperVersions, blob partition managers, direct-write settings, touched managers, and rollback metadata.
- `MaybeTransformBatchForBlobDirectWrite()`, `AppendPreprocessedPutEntityToBatch()`, `AppendSortedPutEntityToBatch()`, `PutEntityFastPath()`, `WritePreprocessedPutEntityBatch()`, and `SyncBlobDirectWriteManagers()` implement wide-column/blob direct-write preprocessing.
- `WriteImpl()` is the main write state machine and dispatches to unordered, pipelined, two-queue WAL-only, or normal group-write paths.
- `PipelinedWriteImpl()`, `UnorderedWriteMemtable()`, and `WriteImplWALOnly()` implement specialized write modes.
- `PreprocessWrite()` handles background-error checks, WAL pressure, write-buffer-manager flushes/stalls, flush scheduling, memtable-history trimming, and WAL sync preparation.
- `MergeBatch()`, `WriteToWAL()`, `WriteGroupToWAL()`, and `ConcurrentWriteGroupToWAL()` flatten write groups, verify checksums, append to WAL, sync WALs/dirs, update WAL sizes, and cache recoverable state.
- `WriteRecoverableState()`, `SelectColumnFamiliesForAtomicFlush()`, `AssignAtomicFlushSeq()`, `SwitchWAL()`, `HandleWriteBufferManagerFlush()`, `DelayWrite()`, `WriteBufferManagerStallWrites()`, `ScheduleFlushes()`, `SwitchMemtable()`, and `GetWalPreallocateBlockSize()` maintain write-side persistence and flow control.

### Control Flow

Single-operation public methods first validate timestamp expectations (`FailIfCfHasTs()` or `FailIfTsMismatchCf()`), then call default `DB` methods that build small `WriteBatch` objects and eventually call `Write()`. `Write()` and `WriteWithCallback()` add per-key protection metadata when requested and delegate to `WriteImpl()`.

`WriteImpl()` begins with guardrails: null batch, missing timestamps, rate-limiter constraints, sync-without-WAL, incompatible pipelined/two-queue/unordered modes, unsupported `DeleteRange` plus row cache, and `WriteBatchWithIndex` restrictions. It traces early when write order need not be preserved, throttles low-priority writes if compaction is behind, handles two-write-queue WAL-only prepares, then prepares blob direct-write state if any CF supports it.

The main mode split is:

- `unordered_write`: write WAL through `WriteImplWALOnly()` with order assignment and publish-last-sequence, then later insert into memtable through `UnorderedWriteMemtable()`.
- `enable_pipelined_write`: `PipelinedWriteImpl()` separates WAL group leadership from memtable writer leadership so WAL and memtable phases can overlap.
- normal path: join `write_thread_`, let followers perform parallel memtable writes when selected, or let the group leader run `PreprocessWrite()`, enter a write group, optionally materialize deferred `PutEntity` and blob-index transformations, assign sequences, write/sync WAL, run pre-release callbacks, insert into memtables serially or in parallel, ingest WBWI data when present, publish `versions_->SetLastSequence()`, and exit the write group.

`PreprocessWrite()` runs before group WAL/memtable application. It checks existing background error state, flushes CFs when WAL bytes exceed `GetMaxTotalWalSize()`, asks the write buffer manager to switch selected memtables when memory pressure is high, trims immutable memtable history, drains the flush scheduler, applies write-controller delay/stall policy, blocks on global write-buffer-manager stalls, and prepares the WAL writer/sync bookkeeping under `wal_write_mutex_`.

WAL writing goes through `MergeBatch()` when a group has multiple valid writers or needs WAL-only append semantics. `WriteToWAL()` verifies the merged batch checksum, emits timestamp-size records when needed, appends to the current log with the assigned sequence, updates `wals_total_size_` and `alive_wal_files_` size state, and records the WAL number. Synchronous writes then sync all relevant logs and optionally fsync the WAL directory before manifesting synced-WAL state.

Memtable switching starts with `WriteRecoverableState()` so transaction recoverable state is present in memtables before an old WAL can be released. `SwitchMemtable()` may wait for an async-precreated WAL or create/recycle one outside the DB mutex, constructs the new memtable, marks the old memtable immutable and fragments range tombstones outside the mutex, installs the new WAL and memtable under locks, updates empty-CF WAL metadata and manifest WAL-deletion records when tracking is enabled, rotates blob direct-write generations, adds old/current and optional WBWI memtables to the immutable list, installs a SuperVersion, schedules async WAL precreation, and notifies listeners.

### State And Persistence Behavior

Persistent state changes include WAL records, optional WAL sync and WAL-directory fsync, MANIFEST edits for synced WAL additions/deletions, memtable contents later flushed to SSTs, blob direct-write files and partition-manager accounting, and persistent stats CF writes. In-memory state includes write-thread queues, `versions_` sequence counters (`LastAllocatedSequence`, `LastPublishedSequence`, `LastSequence`), `logs_`, `alive_wal_files_`, `cur_wal_number_`, `wal_empty_`, `wal_dir_synced_`, `wals_total_size_`, `cached_recoverable_state_`, flush/trim schedulers, write-controller stalls, and SuperVersion/memtable references.

The code is designed so WAL durability precedes memtable publication for normal writes. It avoids publishing `LastSequence` on partial memtable insert failure and escalates WAL or memtable divergence through `error_handler_`. `disableWAL` writes set `has_unpersisted_data_`. Blob direct-write bytes are flushed or synced before the transformed blob indexes are committed; rollback metadata marks blob writes as garbage if later write phases fail.

### Dependencies And Integration Points

The file integrates with `WriteThread`, `WriteBatchInternal`, `ColumnFamilyMemTablesImpl`, `ColumnFamilyData`, `VersionSet`, WAL `log::Writer`, `WritableFileWriter`, `ErrorHandler`, `WriteController`, `WriteBufferManager`, `FlushScheduler`, `TrimHistoryScheduler`, blob direct-write managers/transformers, `WBWIMemTable`, transaction callbacks, tracing, event listeners, statistics/histograms, and sync-point testing. Public API declarations live in `include/rocksdb/db.h`; option constraints interact with `column_family.cc`, `advanced_options.h`, and timestamp comparator settings.

### Risks And Edge Cases

- This file is the correctness boundary between WAL durability, sequence assignment, and memtable visibility. Any mismatch between `seq_per_batch_`, batch counts, `InsertInto()` sequence advancement, and WAL recovery ordering can create lost or duplicated versions.
- `IngestWriteBatchWithIndex()` checks `if (!write_options.disableWAL)` but returns a message saying it does not support `disableWAL=true`; that diagnostic appears inverted relative to the condition and can mislead operators/tests.
- Blob direct-write transformation is intentionally delayed until after `PreprocessWrite()` in the normal path so blob generation matches the target memtable. Reordering this code can make blob indexes point into the wrong generation.
- The comments note `tracer_` bool checks may be thread-unsafe before taking `trace_mutex_`. Existing locking narrows the race for use, but the optimization remains a known concern.
- `WriteToWAL()` returns early on timestamp-size-record failure before releasing `wal_write_mutex_` when `manual_wal_flush_ && !two_write_queues_` if that failure happens after explicit lock acquisition. This path should be scrutinized in tests or refactoring because early returns in locked regions are high risk.
- `SwitchMemtable()` comments flag unresolved earliest-sequence semantics for new memtables and sequence-consuming operations such as ingestion.
- Write stalls use prior batch size for delay decisions; comments acknowledge possible fairness issues where smaller writes expire while larger writes proceed.
- Failure after WAL write but before memtable insert intentionally sets background errors; recovery assumptions depend on callers closing/reopening rather than continuing with divergent in-memory state.
- `WriteStatusCheck()` and `WALIOStatusCheck()` treat some `Busy`/`Incomplete` statuses as non-fatal. Tests must distinguish transient throttling from corruption/IO-fenced failures.

### Test Signals

High-value existing tests are in `db_write_test.cc` for `IngestWriteBatchWithIndex`, write batching, callbacks, WAL behavior, low-priority/no-slowdown behavior, and transaction-related writes; `db_secondary_test.cc` covers WAL replay consumers; blob direct-write tests exercise transformation and garbage accounting; `db_inplace_update_test.cc` covers the concurrency restriction around in-place updates. Additional signals should include fault injection at WAL append/sync, timestamp-size record emission, manual WAL flush locking, blob direct-write post-transform failures, WBWI commit ingestion, atomic flush selection, WAL recycling, async WAL precreate cleanup, and memtable-switch listener callbacks. Static research only; no build or test command was run for this report.
