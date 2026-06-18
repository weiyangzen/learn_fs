
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_verify_test.go

## Purpose
Verifies `snap verify` succeeds on a healthy snapshot and fails after deleting a referenced pack blob.

## Important APIs, Types, And Functions
- `TestSnapshotVerifyTest` creates a repository, snapshots shared data, runs `snap verify`, removes the first blob whose ID starts with `p`, and expects verification failure.

## Control Flow
The test lists blobs, selects a pack blob by prefix, deletes it, then reruns verification.

## State And Persistence Behavior
Directly corrupts repository blob storage by removing a pack blob while leaving snapshot metadata in place.

## Dependencies And Integration Points
Uses `testenv`, blob CLI commands, and format-specific suite flags.

## Risks And Edge Cases
Assumes a `p` blob exists and is referenced by snapshot content rather than snapshot metadata. Blob naming scheme changes could break selection.

## Test Signals
Simple high-signal corruption detection test for snapshot verification.
