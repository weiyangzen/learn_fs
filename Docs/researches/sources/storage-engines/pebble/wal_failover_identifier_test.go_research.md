# sources/storage-engines/pebble/wal_failover_identifier_test.go

## Purpose
Tests Pebble's WAL failover stable identifier mechanism, which protects recovery from accidentally using the wrong secondary WAL directory or mounted disk.

## Important APIs, Types, And Functions
`TestWALFailoverIdentifier` uses public `Open`, `Options`, `WALFailoverOptions`, `wal.Dir`, and `wal.StableIdentifierFilename`. Helper `writeTestIdentifier` writes and syncs a secondary `stable_identifier` file through `vfs.FS`.

## Control Flow
The test has four subtests. First open with failover generates an identifier, writes it to the secondary directory, and records it in the OPTIONS file. A mismatch between an existing secondary identifier and configured `Dir.ID` must fail open with a wrong-disk error. If the primary options lack an identifier but the secondary already has one, open adopts it and persists it in OPTIONS. Reopening a database with a different user-supplied identifier than the recovered OPTIONS value must fail.

## State And Persistence Behavior
The durable state under test is both the secondary `stable_identifier` file and the primary database OPTIONS content. The tests use `vfs.NewMem`, but explicitly create, open, read, and sync identifier files to model the persistence contract.

## Dependencies And Integration Points
Integrates Pebble DB open option parsing, WAL failover directory initialization, OPTIONS serialization, WAL package directory IDs, and `vfs` file APIs.

## Risks And Edge Cases
The critical risk is silently accepting a stale or wrong secondary WAL directory, which could replay unrelated logs or miss required logs. Adoption behavior must distinguish a legitimate existing secondary ID from a conflicting user-provided ID. The test reads OPTIONS by listing for `OPTIONS-` files, so changes in options-file naming would affect it.

## Test Signals
Signals are non-empty generated identifiers, presence of `[WAL Failover]` and `secondary_identifier=...` in OPTIONS, successful adoption of existing IDs, and expected wrong-disk error strings on mismatches.
