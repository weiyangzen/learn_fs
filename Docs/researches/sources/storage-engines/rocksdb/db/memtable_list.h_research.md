# sources/storage-engines/rocksdb/db/memtable_list.h

## Purpose
`memtable_list.h` declares the immutable memtable list abstraction used by RocksDB column families. It exposes read/query APIs through `MemTableListVersion`, mutable lifecycle and flush APIs through `MemTableList`, and the cross-column-family atomic flush install function.

## Important APIs, types, and functions
The scan helper declarations expose conservative overlap tests for bounded `MultiScanArgs`. `MemTableListVersion` is the refcounted read view. Its public APIs are `Get`, `MultiGet`, `GetMergeOperands`, `GetFromHistory`, range tombstone iterator aggregation, point iterator aggregation, aggregate entry/delete/stats queries, earliest/first sequence lookup, list ID accessors, not-flushed/flushed counts, and newest user-defined timestamp lookup.

Private `MemTableListVersion` APIs are available to `MemTableList` and atomic flush: `Add`, `Remove`, `HistoryShouldBeTrimmed`, `TrimHistory`, `GetFromList`, `AddMemTable`, `UnrefMemTable`, `MemoryAllocatedBytesExcludingLast`, `HasHistory`, and `MemtableLimitExceeded`.

`MemTableList` exposes atomics `imm_flush_needed` and `imm_trim_needed`, counts, flush-pending predicates, `PickMemtablesToFlush`, `RollbackMemtableFlush`, `TryInstallMemtableFlushResults`, `Add`, memory/history accessors, `TrimHistory`, unflushed memory/oldest-key-time estimates, explicit `FlushRequested`, trim scheduling, WAL-prep-section computation, memtable ID queries, newest UDT vectors, atomic flush sequence assignment, secondary replay cleanup, and `GetEditForDroppingCurrentVersion`.

`InstallMemtableAtomicFlushResults` is declared as a free function because it coordinates multiple `MemTableList` instances and multiple `ColumnFamilyData` objects.

## Control flow
The header documents the architectural split: `MemTableListVersion` is not thread-safe but immutable while its refcount exceeds one, making it suitable for readers through SuperVersion. `MemTableList` owns the current version and installs a new version under DB mutex when a mutation would otherwise modify a shared view.

Flush flow starts with `imm_flush_needed` or `FlushRequested`, moves through `PickMemtablesToFlush`, then ends in either `TryInstallMemtableFlushResults`, rollback, or atomic install. The public comments specify that memtables can flush concurrently but must be committed to the MANIFEST in FIFO order to preserve crash recovery.

Read flow uses the current version's `Get`, `MultiGet`, `GetMergeOperands`, iterators, and range tombstone aggregators. History flow is explicitly limited to in-memory-only queries such as transaction validation because flushed history duplicates data already persisted in SST files.

## State and persistence behavior
The header identifies the key state variables: `memlist_` for immutable unflushed memtables, `memlist_history_` for flushed retained history, `max_write_buffer_size_to_maintain_` for history memory budgeting, parent memory usage pointer, version refs, and list IDs. `MemTableList` adds minimum merge count, current version pointer, unstarted flush count, commit-in-progress flag, flush-request flag, cached memory/history atomics, and a monotonically increasing list version ID.

Persistence-facing APIs connect immutable memtables to `VersionEdit`, `VersionSet`, WAL retention, prepared transaction tracking, file metadata, DB directory syncing, and flush job info.

## Dependencies and integration points
The declarations depend on logs-with-prep tracking, memtable interfaces, range deletion aggregation, file naming, log buffers, mutexes, RocksDB DB/iterator/options/types, and `autovector`. Forward declarations tie the header to `ColumnFamilyData`, `InternalKeyComparator`, `MergeIteratorBuilder`, `VersionSet`, `FlushJobInfo`, and `FSDirectory`.

## Risks and edge cases
The header's synchronization comments are essential: except for the two atomics, callers must serialize access with DB mutex or write-thread discipline. `FlushRequested` can set the atomic even in benign races, but logic relies on `num_flush_not_started_` for correctness. Atomic flush ID and sequence APIs assume the list is ordered newest-to-oldest. `GetTablesNewestUDT` relies on ascending ID iteration from the back of the list.

## Test signals
`memtable_list_test.cc` maps closely to this API surface. Additional validation should cover SuperVersion ref/unref behavior, iterator reads with range tombstones, transaction validation through history, secondary replay cleanup, atomic flush recovery, and WAL retention with prepared transactions.
