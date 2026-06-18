<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/managed_db_test.go -->
# sources/storage-engines/badger/managed_db_test.go

## Purpose
This file tests managed timestamp behavior, destructive DB operations, prefix dropping, read-only protections, races with concurrent writers/readers, write batch timestamp semantics, duplicate key/version behavior, and discard-stat cleanup.

## Important APIs, Types, And Functions
Helpers `val`, `numKeys`, and `numKeysManaged` create values and count visible keys through ordinary or managed transactions. Tests include `TestDropAllManaged`, `TestDropAll`, `TestDropAllTwice`, `TestDropAllWithPendingTxn`, `TestDropReadOnly`, `TestWriteAfterClose`, `TestDropAllRace`, `TestDropPrefix`, `TestDropPrefixWithPendingTxn`, `TestDropPrefixReadOnly`, `TestDropPrefixRace`, `TestWriteBatchManagedMode`, `TestWriteBatchManaged`, `TestWriteBatchDuplicate`, and `TestZeroDiscardStats`.

## Control Flow
The tests populate temporary DBs with many keys, call `DropAll` or `DropPrefix`, verify counts immediately and after reopen, and then write again to ensure the DB remains usable. Race tests run writer goroutines while drop operations execute. Pending-transaction tests continuously iterate/read from an old transaction while a drop operation runs. Write-batch tests flush large batches under managed timestamps and verify iterator versions.

## State And Persistence Behavior
The suite exercises persistent value-log and LSM recovery across close/reopen, including preservation of the badger head after `DropAll` in managed mode. It verifies that drop operations clear visible keys and zero relevant value-log discard stats. Read-only tests assert destructive operations panic when opened read-only, except for Windows lock limitations.

## Dependencies And Integration Points
It depends on `Open`, `OpenManaged`, `DefaultOptions`, `getTestOptions`, `WriteBatch`, managed transactions, iterators, value-log discard stats, and `z.Closer`. It integrates `managed_db.go` with drop APIs implemented elsewhere and with value-log rewrite/drop state.

## Risks And Edge Cases
The pending transaction tests intentionally run loops until a drop causes read errors, so they validate non-deadlock more than exact snapshot results. Race tests accept write errors during destructive operations and only assert key count decreases. Windows read-only behavior has a special expected error. These are broad integration tests and can be timing-sensitive.

## Test Signals
Important signals are post-drop key counts, ability to write after drops, correct reopen state, `ErrDBClosed` after close, panic on read-only drops, managed write-batch versions, duplicate collapse or retention depending on batch type, and zeroed discard stats after rewrite/drop-all.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/managed_db_test.go -->
