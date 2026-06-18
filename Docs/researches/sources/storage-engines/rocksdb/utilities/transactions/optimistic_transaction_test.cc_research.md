# sources/storage-engines/rocksdb/utilities/transactions/optimistic_transaction_test.cc

## Purpose

This file is a parameterized GoogleTest suite for `OptimisticTransactionDB`. It validates optimistic transaction commit behavior, conflict detection, snapshots, memtable-history validation, column-family independence, untracked writes, savepoints, entity/wide-column APIs, transaction iterators, timestamped-snapshot unsupported paths, and OCC lock bucket behavior. Tests run with both `OccValidationPolicy::kValidateSerial` and `OccValidationPolicy::kValidateParallel`.

## Important APIs, Types, And Functions

- `OptimisticTransactionTest` owns the temporary DB, `Options`, `OptimisticTransactionDBOptions`, and `std::unique_ptr<OptimisticTransactionDB>`.
- `OpenImpl()` opens an OCC DB with explicit column-family descriptors.
- `FlushTest2PopulateTxn()` stages a snapshot read/update sequence reused around memtable flush behavior.
- `OptimisticTransactionStressTestInserter()` drives multi-threaded `RandomTransactionInserter` workloads.
- Public transaction APIs covered include `BeginTransaction`, `GetForUpdate`, `MultiGetForUpdate`, `Put`, `PutEntity`, `Merge`, `Delete`, untracked variants, `SetSnapshot`, `SetSavePoint`, `RollbackToSavePoint`, `UndoGetForUpdate`, `Commit`, `Rollback`, `GetIterator`, `GetCoalescingIterator`, and `GetAttributeGroupIterator`.

## Control Flow

The early tests show the core OCC pattern: transaction reads/writes track keys, external modifications to tracked keys are only detected at `Commit()`, and failed commits return `Busy` without applying any staged changes. Snapshot tests show that the conflict boundary is the snapshot active when the key was tracked; no-snapshot transactions can observe and commit against the latest value.

Flush tests verify that conflict checking can consult flushed memtables while they remain in memtable history, and returns `TryAgain` once history is no longer sufficient. `CheckKeySkipOldMemtable` uses sync points and perf counters to prove the intended number of memtables is checked in history and immutable-memtable paths.

Column-family tests prove key identity includes CF ID, exercise `SliceParts`, `MultiGetForUpdate`, dropped-CF failure, and shared versus non-shared OCC lock bucket pointer space under parallel validation. Iterator/entity tests validate read-your-own-write overlays across DB iterators, multi-CF coalescing, attribute groups, lazy `PrepareValue()`, and invalid argument paths.

## State And Persistence Behavior

The suite repeatedly checks atomicity: failed commits do not leak tracked or untracked writes. Untracked operations are included in the final write batch but intentionally skipped for conflict tracking. Reopen tests guard sequence-number persistence after recovery. Timestamped snapshot tests establish optimistic transactions reject `CommitAndTryCreateSnapshot()` with `InvalidArgument` for missing commit timestamp and `NotSupported` for explicit timestamp.

## Dependencies And Integration Points

The file uses `DBImpl`, `DBTestUtil`, `OptimisticTransactionDB`, `Transaction`, `SyncPoint`, `PerfContext`, `RandomTransactionInserter`, CRC/hash helpers, and RocksDB test harness utilities. It is both public API coverage and implementation-sensitive coverage for memtable history, lock buckets, and internal iterator overlays.

## Risks And Test Signals

Key risks covered are stale memtable history, parallel validation bucket hashing, dropped CF handles, misuse of untracked writes, entity API argument validation, and iterator correctness with transaction-local updates. The stress test runs four threads with 10,000 transactions each over a constrained key space and verifies aggregate consistency.
