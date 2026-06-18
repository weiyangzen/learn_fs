# sources/sync-backup/kopia/tests/end_to_end_test/restore_fail_test.go

## Purpose
Negative restore test that deletes a newly created pack blob and verifies restore failure, then verifies `--ignore-errors` permits best-effort restore.

## Important APIs, Types, and Functions
`TestRestoreFail`, `findPackBlob`, `getNewBlobIDs`, and `parseBlobIDFromBlobList`.

## Control Flow
The test creates a repo and source tree, records blob list before snapshot, snapshots source and parses the manifest from logs, records new blobs, selects a pack blob by prefix regex, deletes it, expects `snapshot restore` failure, then reruns restore with `--ignore-errors` and expects success.

## State and Persistence Behavior
Deletes actual pack content required by the snapshot, creating repository corruption for the target snapshot.

## Dependencies and Integration Points
Exercises blob list/delete, snapshot create/restore, log parsing helper `parseSnapshotResultFromLog`, pack blob naming, and restore error handling.

## Risks
Assumes at least one new pack blob exists and text blob-list parsing returns ID in the first field. Best-effort restore success does not verify output contents.

## Test Signals
Confirms missing content causes restore failure and ignore-errors changes the command outcome.
