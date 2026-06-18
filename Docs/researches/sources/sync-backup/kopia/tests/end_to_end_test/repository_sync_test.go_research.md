# sources/sync-backup/kopia/tests/end_to_end_test/repository_sync_test.go

## Purpose
Tests repository synchronization to another filesystem location and format compatibility checks.

## Important APIs, Types, and Functions
`TestRepositorySync`.

## Control Flow
The test creates a repo, snapshots two shared directories, records source list, syncs blobs to a second directory with timestamps, changes a repository parameter and syncs again, verifies `--must-exist` fails against an empty target, connects to the synced target and checks source count, then creates a separate incompatible repo and verifies syncing it into the target fails.

## State and Persistence Behavior
Copies full repository blob state between filesystem directories, mutates repository parameters, and reconnects the same client to the copied repository.

## Dependencies and Integration Points
Exercises repo sync-to, filesystem storage, repository format parameter changes, snapshot listing, connect, and incompatible format detection.

## Risks
Only source count is compared after sync, not every snapshot/content. Reusing the same test environment after reconnect changes its active repository.

## Test Signals
Confirms sync handles normal and parameter-changed repos, refuses missing targets with `--must-exist`, produces a connectable copy, and rejects syncing incompatible repositories together.
