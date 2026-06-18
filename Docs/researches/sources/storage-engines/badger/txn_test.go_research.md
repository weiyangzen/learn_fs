# sources/storage-engines/badger/txn_test.go

## Purpose
This Go test file validates Badger transaction semantics: write/read visibility, asynchronous commit behavior, MVCC version reads, iterator ordering across versions and deletes, managed timestamp mode, architecture regressions, and conflict detection. It is a behavioral specification for `DB.NewTransaction`, `Update`, `View`, `Commit`, `CommitAt`, `CommitWith`, `Get`, `SetEntry`, `Delete`, and `Iterator`.

## Important APIs, Types, And Functions
Key tests include `TestTxnSimple`, `TestTxnReadAfterWrite`, `TestTxnCommitAsync`, `TestTxnVersions`, `TestTxnWriteSkew`, three iterator edge cases, two `AllVersions` deletion tests, `TestManagedDB`, `TestArmV7Issue311Fix`, and `TestConflict`. The file uses `runBadgerTest`, `getTestOptions`, `DefaultIteratorOptions`, `ErrConflict`, `ErrKeyNotFound`, `y.KeyWithTs`, and `z.Closer`.

## Control Flow
Most tests create a temporary DB, stage transactions, commit them, then open read transactions with explicit read timestamps or iterator options. The async commit test runs a continuous reader while many writers transfer balances and requires the invariant total to remain 4000. Iterator edge cases build small version histories and tombstones, then check forward/reverse seeks and rewinds. Managed mode creates transactions with explicit timestamps and verifies `CommitAt` rather than ordinary `Commit`.

## State And Persistence Behavior
The tests exercise MVCC state in the oracle read timestamp, pending write buffers inside active transactions, in-memory and disk-backed DB modes, and direct LSM insertion of tombstones for an all-versions regression. They do not create long-lived persisted fixtures except through the helper DB lifecycle, but they are sensitive to WAL/LSM visibility and commit ordering.

## Dependencies And Integration Points
The suite integrates transaction code with iterators, the oracle conflict checker, value copying, async commit callback paths, managed timestamp gates, and internal key timestamp encoding. It also validates InMemory mode for selected transaction paths.

## Risks And Edge Cases
Important risks covered are write skew, duplicate concurrent set-if-absent attempts, deleted versions being hidden or exposed under `AllVersions`, and iterator seek behavior when pending writes add/delete nearby keys. The tests intentionally panic on `CommitAt` in unmanaged mode. Remaining gaps include crash recovery for transactions and detailed callback ordering beyond success/failure.

## Test Signals
Failures indicate regressions in MVCC visibility, conflict ranges, iterator merge logic across pending writes and committed tables, async commit atomicity, managed transaction restrictions, or timestamped key ordering.
