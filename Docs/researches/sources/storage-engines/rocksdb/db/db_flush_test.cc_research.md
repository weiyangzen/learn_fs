# sources/storage-engines/rocksdb/db/db_flush_test.cc

## Purpose

`db_flush_test.cc` is a large GoogleTest suite for RocksDB memtable flush behavior. It covers manual and automatic flush scheduling, WAL sync interactions, listener callbacks, memtable garbage accounting, experimental MemPurge, blob flushing, checksum handoff, atomic flush across column families, failure rollback, table-builder error propagation, super-block alignment, and range tombstone ordering. The suite uses extensive sync points and fault-injection environments because many target bugs occur only under precise background-thread interleavings.

## Important APIs, Types, and Helpers

- `DBFlushTest` derives from `DBTestBase` and adds `WaitForFlushCallbacks()` to wait for listener callbacks before closing.
- `DBFlushDirectIOTest`, `DBAtomicFlushTest`, `DBFlushTestBlobError`, and `DBFlushSuperBlockTest` are parameterized fixtures.
- `TestFlushListener` validates `OnTableFileCreated` and `OnFlushCompleted` metadata, write-stall flags, file numbers, blob file numbers, and callback thread IDs.
- `ConditionalUpdateFilter` and `ConditionalUpdateFilterFactory` test flush-time compaction filters, including MemPurge.
- The tests use `FaultInjectionTestEnv`, `FaultInjectionTestFS`, `MockEnv`, `SyncPoint`, `SleepingBackgroundTask`, `TransactionDB`, blob options, checksum handoff options, `FlushOptions`, `ColumnFamilyHandleImpl`, and DBImpl test hooks such as `TEST_WaitForFlushMemTable`, `TEST_SwitchMemtable`, `TEST_AtomicFlushMemTables`, and `TEST_table_cache`.

## Control Flow

Early tests validate scheduler and WAL paths: concurrent flushes while writing MANIFEST, WAL sync failure/skip, low-priority flush fallback when the high-priority pool is empty, close while a low-priority flush is queued, manual flush with `min_write_buffer_number_to_merge`, and scheduling only one background thread.

The statistics tests construct overwrite/delete/range-delete workloads and compare `MEMTABLE_PAYLOAD_BYTES_AT_FLUSH` and `MEMTABLE_GARBAGE_BYTES_AT_FLUSH` against expected byte counts. Listener tests ensure flush-completed callbacks run only after flush results are committed to in-memory version state.

The MemPurge block toggles `experimental_mempurge_threshold`, checks high-garbage overwrite workloads purge in memory without creating SSTs, verifies random inserts still force SST creation, confirms atomic flush disables MemPurge, exercises delete and range-delete semantics with iterators, validates flush-time compaction filters, documents disabled WAL support, checks correct log number/SST creation after chained mempurges, and reproduces a memtable-ID ordering race when MemPurge releases and reacquires the DB mutex.

Blob and checksum sections verify flushing small values to SST and large values to blob files, blob metadata in `VersionStorageInfo`, compaction stats, table-file checksum handoff failures, disabled checksum handoff behavior, descriptor-file checksum handoff failures, and cleanup after blob builder errors.

Atomic flush tests run with `atomic_flush` true and false. They cover manual flush under 2PC, multi-CF manual atomic flush, precomputing min log number to keep, automatic flush triggered by a full memtable, rollback when some jobs complete and later fail, dropped CF races before and after scheduling, close during auto flush, picking memtables while a background flush is paused, rollback after manifest install failure, multi-CF automatic flush failure, manifest write queue wakeup after errors, and no-wait behavior when writes are stopped.

The final regression tests cover non-atomic rollback of pending flushes, aborting new flushes after background errors, avoiding a stuck DB after atomic flush errors, output record-count verification for block-based and plain tables, super-block alignment compatibility/checksums, builder IO-error propagation, table-cache eviction after flush install failure, and range tombstone insertion ordering around `SwitchMemtable`.

## State and Persistence Behavior

The suite observes mutable memtables, immutable memtable queues, WAL numbers/min-log retention, MANIFEST edits, L0 file installation, blob file metadata, table cache contents, background error state, snapshots, and recovered data after reopen. It deliberately creates retryable and fatal IO failures to ensure uninstalled flush outputs are rolled back, obsolete files are released, cached table entries are evicted, WALs remain recoverable, and atomic-flush invariants hold across column families.

## Dependencies and Integration Points

The file integrates with DBImpl flush/compaction scheduling, `VersionSet::LogAndApply`, `MemTableList`, `FlushJob`, `BuildTable`, table builders, blob file builders, `InternalStats`, event listeners, transaction DB 2PC recovery, file checksum handoff, block-based table super-block alignment, range tombstone conversion, write-stall logic, and fault-injection filesystem layers.

## Risks and Edge Cases

The tests target deadlocks, stale memtable IDs, manifest write ordering, dropped-column-family lifetime races, incomplete rollback after partial flush success, background-error recovery loops, false corruption errors that mask IO errors, table-cache leaks after failed installs, snapshot visibility of tombstones, and cross-CF atomicity gaps. Many cases depend on sync-point labels and exact interleavings, so refactors of flush internals can break tests even if external behavior remains correct. The suite also includes environment-sensitive skips for checksum handoff on memory or encrypted environments.

## Test Signals

Signals include `Status` severity checks, file counts per level, ticker counts, listener metadata assertions, sync-point callback counters, blob/table metadata, WAL/min-log values after reopen, successful/failed point reads, iterator results, table-cache entry counts, checksum verification, and absence of hangs in historically deadlocking paths.
