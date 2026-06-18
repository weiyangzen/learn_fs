
# sources/sync-backup/kopia/tests/recovery/recovery_test/recovery_test.go

## Purpose
Exercises recovery behavior after blob deletion, killed maintenance/snapshot processes, snapshot-fix repair commands, and crash consistency after interrupting a snapshot.

## Important APIs, Types, And Functions
- `TestSnapshotFix` sets up snapshots, starts and quickly kills maintenance, deletes a random blob, runs full maintenance, confirms restore fails, extracts object ID from the error, runs `snapshot fix remove-files --object-id`, then restores successfully.
- `TestSnapshotFixInvalidFiles` similarly corrupts a repository and repairs with `snapshot fix invalid-files --verify-files-percent=100`.
- `TestConsistencyWhenKill9AfterModify` creates a baseline snapshot, adds files, connects repo, starts `snap create --json --parallel=1`, kills it when progress indicates hashing/uploading, verifies repository consistency, restores a random snapshot, and compares with baseline data.
- `killOnCondition` monitors stderr and kills the command after snapshot progress starts.
- `CompareDirs` uses `internal/diff` over `localfs` entries.
- `getBlobIDToBeDeleted` parses restore error text for an object ID after `unable to open object`.

## Control Flow
Tests use `blobmanipulator` to prepare data and run high-level operations, then directly spawn external `KOPIA_EXE` commands for maintenance/snapshot interruption. Repair tests intentionally induce corruption and then verify recovery paths by attempting restores before and after fixes.

## State And Persistence Behavior
Uses persistent filesystem repository paths under `repoPathPrefix`, writes large random datasets, deletes pack blobs, deletes snapshots, runs maintenance with no safety, and stores/restores snapshot metadata. Crash-consistency test mutates source data and ensures interrupted writes do not corrupt existing snapshots.

## Dependencies And Integration Points
Depends on `KOPIA_EXE`, FIO availability through `blobmanipulator`, `kopiarunner`, `testenv.TestRepoPassword`, `internal/diff`, `localfs`, and OS process control.

## Risks And Edge Cases
Timing is intentionally racy: maintenance is killed after 10 ms, and snapshot kill depends on matching progress text containing `hashing`, `hashed`, and `uploaded`. Error parsing in `getBlobIDToBeDeleted` is coupled to human error text. Tests can be expensive due to 40 MB and 200 MB-scale random file generation.

## Test Signals
High-value recovery/crash-consistency signal for repair commands and repository robustness after abrupt process death.
