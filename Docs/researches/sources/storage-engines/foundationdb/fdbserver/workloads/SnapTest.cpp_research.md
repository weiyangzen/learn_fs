# sources/storage-engines/foundationdb/fdbserver/workloads/SnapTest.cpp

## Purpose
`SnapTestWorkload` orchestrates snapshot creation and validation across restart phases. Different `testID` values create pre-snapshot keys, take a snapshot, create post-snapshot keys, validate restored state, or test rejection of a non-whitelisted snapshot command.

## Important APIs, Types, And Functions
It derives from `TestWorkload` and registers as `SnapTest`. Important state includes `numSnaps`, `maxSnapDelay`, `testID`, `snapUID`, `restartInfoLocation`, `retryLimit`, `snapSucceeded`, and `attemptDuplicateSnapshot`. Key actors are `_create_keys` and `_start`, using `snapCreate`, `CSimpleIni`, `SERVER_KNOBS->SNAP_MINIMUM_TIME_GAP`, and normal-key range scans.

## Control Flow
Only client 0 runs. For `testID=0`, it writes 1000 even `snapKey` entries. For `testID=1`, it waits a random delay, calls `/bin/snap_create.sh` with a random UID, optionally submits a duplicate snapshot request, retries according to `retryLimit`, and stores `RestoreSnapUID` plus `BackupFailed` in restart info. For `testID=2`, it writes 1000 odd entries after the snapshot. For `testID=3`, it skips validation if snapshot failed, otherwise scans `normalKeys` and verifies all `snapKey` IDs are even and value-equal. For `testID=4`, it verifies a non-whitelisted path fails.

## State And Persistence Behavior
The workload writes `snapKey*` records into normal keyspace and writes snapshot metadata to the restart INI file. It also modifies simulation policy by disabling log set kills. Snapshot data is external to normal transactions and consumed by later restart phases.

## Dependencies And Integration Points
It integrates with ManagementAPI snapshot creation, restart metadata, simulation policy, SimpleIni, and tester failure-injection controls. It disables `RandomMoveKeys` and `Attrition` because data movement and missing machines can make snapshot state incomplete.

## Risks And Edge Cases
Only `numSnap=1` validation is noted as currently supported. Duplicate snapshot handling expects either duplicate request behavior or the latest request to complete. Snapshot creation can fail for many reasons, so retries may run indefinitely when `retryLimit=-1`. Validation assumes exactly 1000 pre-snapshot keys and no odd post-snapshot keys after restore.

## Test Signals
`SnapshotCreateStatus` records success or failure. `check` returns `snapSucceeded` for `testID=1`. Restore validation failures emit `SnapTestVerifyCntValue` or throw `operation_failed`; unsupported path tests assert expected snapshot errors.
