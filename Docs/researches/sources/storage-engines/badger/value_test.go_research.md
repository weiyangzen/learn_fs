# sources/storage-engines/badger/value_test.go

## Purpose
This large test file specifies Badger value-log behavior: basic writes/reads, GC rewrite correctness, managed-mode GC, discard stats persistence, checksum/truncation recovery, memtable corruption recovery, dynamic threshold behavior, value-log metadata bits, overflow validation, and first-file numbering.

## Important APIs, Types, And Functions
Core tests include `TestValueBasic`, `TestValueGCManaged`, `TestValueGC` through `TestValueGC4`, `TestPersistLFDiscardStats`, `TestValueChecksums`, `TestPartialAppendToWAL`, `TestReadOnlyOpenWithPartialAppendToWAL`, `TestPenultimateMemCorruption`, `TestValueGCRewriteSkipsLSMGetOnlyForExpiredEntriesInMixedVlogFile`, `TestBug578`, `TestValueLogTruncate`, `TestSafeEntry`, `TestValueEntryChecksum`, `TestValidateWrite`, `TestValueLogMeta`, and `TestFirstVlogFile`. Helpers include `createMemFile`, `checkKeys`, and `testHelper`.

## Control Flow
The tests create temporary DBs with small value-log/table thresholds, write large values to force vlog pointers, delete or overwrite subsets, invoke `vlog.rewrite` or `RunValueLogGC`, close/reopen, and verify reads. Recovery tests construct or corrupt `.mem` files to simulate partial appends and checksum failures. The mixed expired/live rewrite test clears expvar metrics and asserts only non-expired entries trigger LSM gets.

## State And Persistence Behavior
Persistent state includes value logs, memtable WAL files, SSTs, discard-stat logs, and DB reopen behavior. Several tests deliberately avoid clean close or release locks to simulate crashes. `TestPersistLFDiscardStats` captures discard stats on close and compares them after reopen. `TestValueLogMeta` verifies transaction bits are stripped from vlog records while LSM entries retain the transaction bit.

## Dependencies And Integration Points
The file exercises transaction write/delete APIs, internal `valueLog` and `logFile` methods, memtable WAL paths, expvar metrics, compaction/flattening, checksum verification, and iterator APIs. It uses `humanize`, `reflect`, and Badger test helpers.

## Risks And Edge Cases
Covered risks include stale versions after GC (#578), iterators reading through GC, partially written or corrupted WAL entries, read-only open when truncation would be required, value-pointer offset overflow, and corrupt value bytes. Some tests are skipped or contain TODOs around broken checksum error propagation and difficult value-log trigger reproduction.

## Test Signals
Failures reveal regressions in value-log append/read encoding, GC liveness decisions, crash recovery truncation, discard-stat durability, metrics behavior during rewrite, transaction metadata handling, and file ID initialization.
