# sources/storage-engines/rocksdb/db/memtable_list_test.cc

## Purpose
`memtable_list_test.cc` unit-tests immutable memtable list behavior outside the full DB flush machinery. It constructs real `MemTable` objects, mock `VersionSet` state, and test column families to validate reads, history retention, flush scheduling, manifest installation, atomic flush, refcount cleanup, and user-defined timestamp tracking.

## Important APIs, types, and functions
`MemTableListTest` owns temporary DB state, options, column-family handles, and an atomic file-number generator. `CreateDB` opens a DB with default and two additional column families, optionally using a comparator with 64-bit user-defined timestamps.

`Mock_InstallMemtableFlushResults` builds a minimal `VersionSet`, default `ColumnFamilyData`, mutex, log buffer, file number, and flush job list, then invokes `MemTableList::TryInstallMemtableFlushResults`. `Mock_InstallMemtableAtomicFlushResults` creates matching CF metadata, dummy `FileMetaData` objects, and calls `InstallMemtableAtomicFlushResults`.

The tests are `Empty`, `GetTest`, `GetFromHistoryTest`, `FlushPendingTest`, `EmptyAtomicFlushTest`, `AtomicFlushTest`, `GetTableNewestUDT`, and `ConcurrentGetTableNewestUDT`.

## Control flow
`GetTest` starts with an empty list, creates skiplist memtables, inserts deletes, puts, preferred-seqno values, and merge operands, then validates direct memtable reads and list reads. It confirms newer immutable memtables override older ones, historical sequence lookups can see older values, and merge operands across memtables are combined through the configured string append operator.

`GetFromHistoryTest` configures a positive `max_write_buffer_size_to_maintain`, flushes memtables into history through the mock install path, verifies that normal `Get` no longer sees flushed data while `GetFromHistory` does, then adds another memtable to force history trimming and deletion of the oldest retained memtable.

`FlushPendingTest` builds six memtables and exercises transitions between requested flushes, threshold-triggered flushes, picked in-progress memtables, rollback, non-consecutive pick avoidance, out-of-order flush completion, FIFO commit installation, max memtable ID filtering, history retention, and final refcount deletion.

`AtomicFlushTest` constructs three independent `MemTableList`s, selects different flush ranges per column family, installs them atomically, and checks file numbers, not-flushed counts, and cleanup after unref.

Timestamp tests write keys with appended 64-bit timestamps and verify `GetTablesNewestUDT` returns per-table newest values in ascending ID order. The concurrent variant writes from multiple threads with concurrent memtable insert enabled, calls `BatchPostProcess`, and checks the atomically tracked maximum timestamp.

## State and persistence behavior
The tests intentionally exercise state that persists across memtable lifecycle transitions: `flush_in_progress_`, `flush_completed_`, file numbers, memtable IDs, list history, memory retention limits, `imm_flush_needed`, `flush_requested_`, `num_flush_not_started_`, `VersionEdit` installation, and refcounts. Mock `VersionSet::Recover` provides enough MANIFEST/WAL state to validate install logic without a full flush job.

## Dependencies and integration points
The test includes merge context, version set, write controller, write buffer manager, RocksDB DB/status APIs, test harness utilities, string utilities, and merge operators. It depends on real `MemTable` insertion and read code, real `VersionSet` recovery/logging paths, and real column-family handles.

## Risks and edge cases
The mock install helpers assume default CF layout and generated file metadata are sufficient for the install path. Tests directly call internal memtable APIs, so missing calls such as `ConstructFragmentedRangeTombstones` would trip assertions not seen through normal DB code. The out-of-order flush scenarios are critical because an apparent success can still leave newer memtables waiting for older commits.

## Test signals
This file itself is the primary test signal for `memtable_list.{h,cc}`. Passing it gives confidence in point lookup ordering, merge-through-list behavior, history retention/trimming, flush-pending state, rollback, FIFO flush result installation, atomic flush coordination, refcount reclamation, and UDT concurrency. Complementary DB-level tests should still cover crash recovery, actual SST creation, range tombstones, and column-family drop races.
