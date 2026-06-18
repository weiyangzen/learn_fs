# sources/storage-engines/foundationdb/fdbserver/workloads/RestoreMultiRanges.cpp

## Purpose
`RestoreMultiRangesWorkload` verifies that restoring a subset of backed-up ranges restores only the selected keys. It backs up keys in `[a,z)`, clears the database, restores two disjoint subranges, and checks that key `b` was skipped.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `RestoreMultiRanges`. Important functions are `clearDatabase`, `prepareDatabase`, `logTestData`, `verifyDatabase`, and `_start`. It uses `FileBackupAgent`, `IBackupContainer`, `BackupContainerFileSystem::createTestEncryptionKeyFile`, `submitBackup`, `waitBackup`, and `restore`.

## Control Flow
Client 0 clears normal keys, writes five known keys (`a`, `aaaa`, `b`, `bb`, `bbb`), optionally creates an encryption key file, and submits a stop-when-done backup over `[a,z)`. After waiting for completion, it clears the database and restores `[a,aaaaa)` plus `[bb,bbbbb)`. `check` runs `verifyDatabase`, expecting exactly four keys: `a`, `aaaa`, `bb`, and `bbb`.

## State And Persistence Behavior
The workload intentionally creates, removes, and restores normal-key data. It writes backup files under `file://simfdb/backups/` and may create a simulation encryption key file. Restore runs with database lock/unlock enabled and without applying mutation logs only.

## Dependencies And Integration Points
It integrates with the file backup agent, file-system backup container, encryption test utilities, and the tester workload lifecycle. It exercises the restore overload that accepts an explicit `VectorRef<KeyRangeRef>` range list.

## Risks And Edge Cases
It tolerates `backup_unneeded` and `backup_duplicate` on submission. The verification only checks key order and membership, not values, although the prepared values match keys. A range boundary bug would show up because `b` sits outside both restore ranges while nearby `bb` and `bbb` should restore.

## Test Signals
Success traces include `RestoreMultiRanges_VerifyPassed` and `RestoreMultiRanges_Success`. Failure emits `TestFailureInfo` and `CurrentDataEntry` traces with actual range contents. `check` returns the verifier result.
