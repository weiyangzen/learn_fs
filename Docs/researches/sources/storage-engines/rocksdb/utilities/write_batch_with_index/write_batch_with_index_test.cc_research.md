<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_test.cc -->
# sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_test.cc

## Purpose
This is RocksDB's broad regression suite for `WriteBatchWithIndex`, its indexed write-batch iterators, point lookups, merge handling, timestamped column-family behavior, wide-column/entity reads, and the `WBWIMemTable` adapter. It validates both overwrite-key and keep-all-updates modes via the parameterized `WriteBatchWithIndexTest`, plus overwrite-specific mutation tests and separate memtable tests.

## Important APIs, Types, And Functions
Key local helpers are `ColumnFamilyHandleImplDummy`, `Entry`, `TestHandler`, and `KVIter`. `ColumnFamilyHandleImplDummy` supplies column-family IDs and comparators without a real DB column family. `TestHandler` replays the underlying `WriteBatch` and counts per-key updates. `KVIter` is a map-backed `Iterator` with optional `allow_unprepared_value` and forced `PrepareValue()` corruption paths, used to model base iterators.

The tests exercise `WriteBatchWithIndex` APIs including `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, `SetSavePoint`, `RollbackToSavePoint`, `Clear`, `NewIterator`, `NewIteratorWithBase`, `GetFromBatch`, `GetFromBatchAndDB`, `GetEntityFromBatch`, `GetEntityFromBatchAndDB`, `MultiGetFromBatchAndDB`, `MultiGetEntityFromBatchAndDB`, `GetCFStats`, and access to the underlying `WriteBatch`. Internal-facing coverage reaches `WBWIIteratorImpl::NextKey`, `PrevKey`, `FindLatestUpdate`, `GetUpdateCount`, and `WBWIMemTable::{Get,MultiGet,NewIterator,AssignSequenceNumbers}`.

## Control Flow
`WBWIBaseTest` creates a temporary per-thread DB path, installs the string-append merge operator, and constructs `batch_` with the parameterized overwrite setting. Its destructor checks that WBWI operation count matches the write-batch count and destroys any opened DB. Many tests build an expected `KVMap` or vector of expected internal keys, then compare iterator walks, seeks, reverse seeks, and point lookups against that expected state.

Early tests cover secondary-index ordering, column-family-specific comparators, duplicate-key overwrite behavior, `WBWIIteratorImpl` key-level navigation, and random base/delta iterator interleavings. Mid-file tests cover `GetFromBatch*`, merge resolution with and without DB state, snapshots, pinned results, mutation while iterating, `ReadOptions` bounds, savepoints, single-delete semantics, and `MultiGet`. Later tests cover merge edge cases, bad merge operators, timestamp update/index behavior, wide-column `PutEntity` and entity read APIs, invalid-argument sanity checks, and column-family statistics. The final `WBWIMemTableTest` section treats a `WriteBatchWithIndex` as a memtable, assigning sequence number ranges and verifying point reads, `MultiGet`, internal iterators, overwritten single-delete emission, and merge operand propagation.

## State And Persistence Behavior
Most state is in-memory in `WriteBatchWithIndex`, its skip-list/index, the underlying `WriteBatch`, local maps, merge contexts, iterator objects, and `WBWIMemTable`. Several tests open an actual temporary RocksDB instance at `test::PerThreadDBPath("write_batch_with_index_test")`, write/flush data, use snapshots, and then clean up the DB in the fixture destructor. Savepoint tests verify that rollback restores indexed state as well as batch state. Memtable tests assign synthetic sequence ranges and inspect internal keys to ensure updates, deletions, overwritten single deletes, and merges get correct visibility and ordering.

## Dependencies And Integration Points
The file depends on RocksDB test infrastructure (`db_test_util`, `testharness`, `testutil`, `SyncPoint`, stack traces), core DB APIs, column-family internals, `WBWIMemTable`, merge operators, wide-column support, timestamp comparators, internal keys, arenas, and `MultiGetContext`. It integrates directly with the public `WriteBatchWithIndex` API and with internal implementation details from `write_batch_with_index_internal.h`, making it a compatibility guard for both user-visible behavior and internal iterator/memtable contracts.

## Risks
The suite is intentionally high-blast-radius: small ordering changes in `WriteBatchWithIndex`, comparator handling, merge operand order, savepoint restoration, timestamp stripping, or base/delta iterator bounds can break many assertions. Tests that mutate a batch while iterating validate single-thread behavior but should not be read as a thread-safety guarantee. The memtable tests rely on detailed sequence-number assignment conventions; implementation changes there require carefully updating expected internal keys. Randomized loops use fixed seeds, giving reproducible coverage but not exhaustive fuzzing.

## Test Signals
The file itself is a test binary: `main()` installs the RocksDB stack trace handler, initializes GoogleTest, and runs all tests. Strong signals include parameterized execution for overwrite modes, deterministic random seeds, explicit status checks, DB-backed merge/snapshot/flush scenarios, SyncPoint corruption injection for blob-backed `PrepareValue`, million-iteration mutation stress, and direct validation of `WBWIMemTable` `Get`, `MultiGet`, and iterator results.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/write_batch_with_index/write_batch_with_index_test.cc -->
