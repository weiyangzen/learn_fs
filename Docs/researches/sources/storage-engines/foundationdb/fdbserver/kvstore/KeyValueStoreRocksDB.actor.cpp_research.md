# sources/storage-engines/foundationdb/fdbserver/kvstore/KeyValueStoreRocksDB.actor.cpp

## Purpose

`KeyValueStoreRocksDB.actor.cpp` implements FoundationDB's RocksDB-backed `IKeyValueStore` when `WITH_ROCKSDB` is enabled. It adapts FDB's asynchronous storage engine contract to RocksDB by wrapping the RocksDB `DB` and FoundationDB column family in reader and writer thread-pool actions, translating FDB key/value operations into RocksDB `WriteBatch`, `Get`, iterator, delete-range, checkpoint, restore, SST ingestion, and compaction calls. The public factory `keyValueStoreRocksDB(...)` constructs `RocksDBKeyValueStore`; if the binary was not built with RocksDB support, it logs `RocksDBEngineInitFailure` and asserts.

The file is also the local integration point for RocksDB configuration knobs, RocksDB background-error propagation, disk metrics, Flow histograms, read queue throttling, checkpoint metadata conversion, and unit tests for basic storage behavior, reopen persistence, checkpoint/restore, range clear pressure, and external SST ingestion.

## Important APIs, Types, and Functions

- `SharedRocksDBState` owns reusable RocksDB options derived from `SERVER_KNOBS`: `DBOptions`, `ColumnFamilyOptions`, `ReadOptions`, `FlushOptions`, and a closing flag plus `lastFlushTime_`. Its `initialCfOptions()` configures compaction style, cache, bloom/prefix behavior, protection bytes, block table factory, file sizing, TTL/periodic compaction, and compact-on-deletion collectors. `initialDbOptions()` configures direct IO, WAL recovery/retention, statistics, logs, background parallelism, rate of open files, checksum factory, and log forwarding.
- `RocksDBErrorListener` converts RocksDB background IO/corruption errors into FDB `io_error`, `file_corrupt`, or `unknown_error` through a `ThreadReturnPromise<Void>`, feeding `IKeyValueStore::getError()`.
- `RocksDBEventListener` records flush completion time for the optional manual flush actor.
- `getMetaData()` and `populateMetaData()` translate between FDB `RocksDBColumnFamilyCheckpoint` / `LiveFileMetaData` serialization and RocksDB `ExportImportFilesMetaData`.
- `ReadIterator` and `ReadIteratorPool` manage RocksDB iterators for range reads. The pool can reuse unbounded iterators, bounded iterators whose stored `KeyRange` contains the request range, or create one-shot bounded iterators depending on knobs. `update()` invalidates reusable iterators after writes, and `refreshIterators()` drops old or invalidated entries.
- `PerfContextMetrics` maps RocksDB perf-context counters into a per-reader/per-writer vector and emits aggregate and per-thread trace details.
- `refreshReadIteratorPool()`, `flowLockLogger()`, `manualFlush()`, and `rocksDBMetricLogger()` are long-running actors for iterator cleanup, FlowLock queue logging, periodic/manual flush, and RocksDB property/statistics telemetry.
- `RocksDBKeyValueStore::Writer` is an `IThreadPoolReceiver` responsible for opening/closing DB handles, committing write batches, exporting/importing checkpoints, restoring, ingesting SST files, and compacting ranges. Nested actions include `OpenAction`, `CommitAction`, `CloseAction`, `CheckpointAction`, `RestoreAction`, `IngestSSTFilesAction`, and `CompactRangeAction`.
- `RocksDBKeyValueStore::Reader` is an `IThreadPoolReceiver` responsible for `ReadValueAction`, `ReadValuePrefixAction`, and `ReadRangeAction`, including optional cache-result behavior, request timeouts, histogram sampling, debug trace batches, and RocksDB perf context sampling.
- `RocksDBKeyValueStore` implements the FDB-facing `IKeyValueStore` surface: `init`, `close`, `dispose`, `onClosed`, `getError`, `getType`, `supportsSstIngestion`, `set`, `clear`, `canCommit`, `commit`, `readValue`, `readValuePrefix`, `readRange`, `getStorageBytes`, `checkpoint`, `restore`, `deleteCheckpoint`, `ingestSSTFiles`, and `compactRange`.

## Control Flow

Construction builds shared RocksDB state, creates a `ReadIteratorPool`, creates read/fetch `FlowLock`s from RocksDB queue knobs, installs a background error listener, initializes histograms if sampling is enabled, and creates a writer plus `ROCKSDB_READ_PARALLELISM` readers. In simulation, the pools are `CoroThreadPool`s so blocking RocksDB operations run on the simulated network thread; otherwise generic thread pools are used with RocksDB-specific thread priorities.

`init()` posts `Writer::OpenAction`. Opening lists existing column families, ensures `"default"` is present, opens all handles with the configured options/listeners/rate limiter, selects or creates `SERVER_KNOBS->DEFAULT_FDB_ROCKSDB_COLUMN_FAMILY`, and starts metrics, FlowLock logging, iterator refresh, and manual-flush actors. `init()` is idempotent by caching `openFuture`.

Writes are staged in a member `rocksdb::WriteBatch`. `set()` lazily creates the batch and records key writes when single-key delete conversion is enabled. `clear()` adds either point deletes or delete ranges; for range clears it can scan existing keys and recently written keys to convert a limited number of ranges into point deletes before falling back to `DeleteRange`. `commit()` posts `CommitAction`, moves out the batch, samples delete histograms, preserves `previousCommitKeysSet` while the commit is in flight, then clears it after the writer completes. `CommitAction` optionally samples perf context and histograms, inspects the batch for range deletes when `ROCKSDB_SUGGEST_COMPACT_CLEAR_RANGE` is enabled, writes with `sync = !ROCKSDB_UNSAFE_AUTO_FSYNC`, invalidates the iterator pool, sends completion, and optionally calls `SuggestCompactRange` for each range delete.

Reads are posted to the read thread pool. For normal throttled reads, `readValue`, `readValuePrefix`, and `readRange` first check waiter counts and acquire either the read or fetch `FlowLock` with `ROCKSDB_READ_QUEUE_WAIT`; eager and system-key reads bypass throttling. Reader actions perform RocksDB `Get` or iterator scans with optional cache fill behavior. Range reads support forward and reverse limits, enforce row/byte limits, set `RangeResult::more`, return iterators to the pool, and can emit queue, action, latency, bytes, and row-count histograms.

`canCommit()` polls RocksDB estimated pending compaction bytes and immutable memtable count. In production it delays a bounded number of times while thresholds indicate overload; in simulation it randomly exercises the overloaded branch because the RocksDB metadata is nondeterministic.

Closing uses `doClose()`: mark shared state closing, stop metrics, stop readers, post a writer close, stop the writer, fulfill `closePromise`, delete the DB wrapper, and optionally destroy the RocksDB database. `deleteCheckpoint()` erases exported column-family checkpoint directories for `DataMoveRocksCF`.

Checkpointing uses RocksDB's checkpoint API. `CheckpointAction` reads the persisted version key `\xff\xffVersion`, validates it against the requested version or `latestVersion`, and either exports the active column family as `DataMoveRocksCF` with serialized live-file metadata or creates a RocksDB checkpoint directory for the older `RocksDB` format. Restore validates all checkpoint formats match. `DataMoveRocksCF` restore drops the current FoundationDB column family, imports the exported metadata into a new column family with `move_files = true`, and replaces the active handle. `RocksDB` restore creates the column family if needed and ingests fetched SST files with `write_global_seqno = false`.

## State and Persistence Behavior

Persistent user data lives in the RocksDB database at `path`, specifically in `SERVER_KNOBS->DEFAULT_FDB_ROCKSDB_COLUMN_FAMILY`. The file creates and stores all updates through RocksDB's WAL and LSM mechanisms. `WriteOptions::sync` follows `ROCKSDB_UNSAFE_AUTO_FSYNC`; disabling sync trades durability for performance. The special key `\xff\xffVersion` is read during checkpoint creation to stamp checkpoint metadata.

The in-memory state includes the active `rocksdb::DB*`, active column-family handle, all column-family handles, current `WriteBatch`, sets tracking keys written in the current and previous commit, delete counters, read/fetch locks, thread-pool references, shared options, listener futures, iterator pool, metric promise streams, and histograms. Iterator reuse state is deliberately invalidated on commit so long-lived iterators do not serve stale snapshots after writes.

Checkpoints are persisted outside the live DB path under the requested checkpoint directory. `DataMoveRocksCF` exports the column family and serializes enough file metadata for later `CreateColumnFamilyWithImport`; `RocksDB` checkpoints serialize a directory and SST file list. Restoring `DataMoveRocksCF` is destructive to the current active column family; restoring `RocksDB` is additive through external SST ingestion.

Storage accounting reports filesystem free/total bytes and RocksDB live plus obsolete SST file sizes. In simulation, live file size is generated from disk usage with deterministic randomness to avoid relying on nondeterministic RocksDB metadata.

## Dependencies and Integration Points

The implementation depends on RocksDB C++ APIs for DB options, block table options, listeners, statistics, perf context, checkpoints, import/export metadata, external SST files, compaction, and rate limiting. It integrates with FDB through `IKeyValueStore`, `CheckpointMetaData`, `CheckpointRequest`, `RocksDBCheckpointUtils`, `BulkLoadFileSetKeyMap`, `FlowLock`, thread pools, actors, `TraceEvent`, histograms, `SERVER_KNOBS`, and simulation helpers.

The file also relies on `RocksDBCommon` for slice conversion, WAL recovery mode, compaction priority, index type, and background error reason names. `RocksDBLogForwarder` bridges RocksDB logging into FDB trace logs. `FDBRocksDBVersion.h` supplies compile-time version checks that must match the included RocksDB headers.

Operational integration points include:

- `getError()` for background storage failure propagation to storage server logic.
- `supportsSstIngestion()`, `ingestSSTFiles()`, and `compactRange()` for bulk-load and physical shard movement workflows.
- `checkpoint()`, `restore()`, and `deleteCheckpoint()` for backup/data movement/checkpoint consumers.
- `getStorageBytes()` for storage capacity accounting.
- Trace events and histograms for monitoring read/write latency, queueing, cache behavior, compaction pressure, iterator reuse, and RocksDB internal metrics.

## Risks and Edge Cases

- The entire implementation is gated by `WITH_ROCKSDB`; callers expecting RocksDB support will assert if the binary lacks it.
- Threading is delicate: RocksDB callbacks can run on background threads, metrics futures retain DB references, and the code explicitly stops metrics before DB deletion.
- Reusable iterators are invalidated asynchronously on writes. Incorrect knob combinations or missed invalidation could cause stale reads, while excessive reuse could pin resources. The constructor logs a warning if both unbounded and bounded reuse knobs are enabled.
- Range clear conversion reads RocksDB while building the write batch. It can increase write latency and depends on `maxDeletes`, `keysSet`, and `previousCommitKeysSet` to avoid missing keys written around an in-flight commit.
- Background errors are mapped broadly; anything other than RocksDB IO/corruption becomes `unknown_error`.
- `ReadOptions::deadline` is computed from timeout knobs and queue wait; timeout paths translate to `transaction_too_old`, so tuning affects apparent transaction age behavior.
- `DataMoveRocksCF` restore drops the current column family before importing. Import failure after the drop leaves the store without the previous active column family.
- Manual flush timing is made deterministic in simulation unless nondeterminism is explicitly enabled; production and simulation behavior intentionally diverge.
- Checkpoint versioning relies on the persisted version key being present or falling back to `latestVersion`.
- `deleteCheckpoint()` only handles `DataMoveRocksCF`; `RocksDB` format deletion is not implemented.

## Test Signals

The file contains `noSim` unit tests:

- `RocksDBBasic` covers set, commit, readValue, single-key clear, range clear, close/dispose, and deletion.
- `RocksDBReopen` verifies persistence across close/reopen and idempotent `init()`.
- `CheckpointRestoreColumnFamily` verifies `DataMoveRocksCF` export/import into another RocksDB store.
- `CheckpointRestoreKeyValues` verifies checkpoint reader visibility of key/value data exported from RocksDB.
- `RangeClear` stress-tests repeated prefix range clears after reads and writes, with a TODO noting possible OOM without memtable flush.
- `IngestSSTFileVisibility` builds an SST with `SstFileWriter`, ingests it through the bulk-load API, and verifies the key is readable.

Additional coverage is implied through chaos/background-error testing comments, trace `CODE_PROBE`s in perf/timeout paths, simulation-specific throttling/overload branches, and FoundationDB storage engine integration tests that instantiate `IKeyValueStore` implementations.
