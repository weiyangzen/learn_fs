# sources/storage-engines/badger/db_test.go

## Purpose
`db_test.go` is the main Badger database API and integration test suite. It covers ordinary and concurrent reads/writes, iterator behavior, transaction limits, loading/reopen, value-log GC, read-only locking, LSM-only mode, sequences, sync/checksum behavior, namespace bans, cache sizing, close races, and package examples.

## Important APIs, Types, and Functions
- Test helpers: `waitForMessage`, `summary`, `getTestOptions`, `getItemValue`, `txnSet`, `txnDelete`, `runBadgerTest`, `dirSize`, `randBytes`, `removeDir`.
- Core API tests: `TestWrite`, `TestUpdateAndView`, `TestConcurrentWrite`, `TestGet`, `TestGetAfterDelete`, `TestTxnTooBig`.
- Iterator and load tests: `TestReverseIterator`, `TestIterate2Basic`, `TestLoad`, `TestIterateDeleted`, `TestIterateParallel`, `TestIteratorPrefetchSize`.
- Persistence and GC tests: `BenchmarkDbGrowth`, `TestDeleteWithoutSyncWrite`, `TestExpiryImproperDBClose`, `TestForceFlushMemtable`, `TestCompactL0OnClose`.
- Locking/lifecycle tests: `TestPidFile`, `TestReadOnly`, `TestOpenDBReadOnly`, `TestCloseDBWhileReading`, `TestIsClosed` in `db2_test.go`.
- Feature tests: `TestSequence*`, `TestLSMOnly`, `TestMinReadTs`, `TestSyncFor*`, `TestVerifyChecksum`, `TestBannedPrefixes`, `TestIterateWithBanned`, `TestBannedAtZeroOffset`.
- Documentation examples: `ExampleOpen`, `ExampleTxn_NewIterator`.

## Control Flow and State
The test flow repeatedly creates temporary directories, opens Badger with mode-specific options, executes transactional writes and reads, then validates behavior through public APIs or carefully chosen internals. Some tests manipulate memtables or filesystem permissions to assert recovery and read-only behavior. Namespace-ban tests build namespaced keys, call `BanNamespace`, and validate both direct operations and iterator skipping. Close-race tests run concurrent `View` loops until `DB.Close` makes reads return `ErrDBClosed`.

## Persistence Behavior
This suite verifies reopening with and without encryption/compression, read timestamp recovery, value-log persistence after unsynced deletes, directory creation, checksum verification, sync visibility, memtable flush state, filesystem read-only permissions, and table-file garbage collection via `levelsController.getSummary`. It also checks that read-only opens can coexist while write opens are excluded on supported platforms.

## Dependencies and Integration Points
It integrates nearly every public Badger API: `Open`, `OpenManaged`, transactions, write batches, stream/managed write batches, iterators, sequences, `Flatten`, `RunValueLogGC`, `StreamDB`, `VerifyChecksum`, `CacheMaxCost`, namespace banning, and `Sync`. It depends on `options`, `pb`, `y`, `z.Buffer`, the filesystem, and `testify/require`.

## Risks and Edge Cases
Several tests are intentionally manual because they are expensive or long running. The suite reaches into internal fields (`db.orc`, `db.mt`, `db.imm`, `lc`, `nextMemFid`), which gives strong regression coverage but couples tests to implementation. Time-based TTL and goroutine leak tests can be sensitive to scheduling. Read-only behavior differs on Windows/Plan9 through platform-specific errors.

## Test Signals
This is the primary automated health signal for Badger's public API and many storage invariants. It includes benchmarks and manual stress tests that complement normal unit coverage, plus examples that validate user-facing documentation output.
