
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_delete_test.go

## Purpose
Tests snapshot deletion commands, dry-run behavior, manifest type safety, restore behavior after deletion, garbage collection interaction, and deleting all snapshots for a source.

## Important APIs, Types, And Functions
- `deleteArgMaker` abstracts command construction for manifest removal, dry-run delete, actual delete, legacy unsafe source flag, object ID delete, and invalid ID cases.
- `TestSnapshotDelete` iterates delete argument variants through `testSnapshotDelete`.
- `TestSnapshotDeleteTypeCheck` ensures non-snapshot manifests such as policy/maintenance cannot be deleted via `snapshot delete`.
- `TestSnapshotDeleteRestore` verifies restore by root ID works before deletion, restore by snapshot ID fails after deletion, repeated deletion fails, and root object restoration remains possible after full maintenance.
- `TestDeleteAllSnapshotsForSource` validates dry-run versus actual `--all-snapshots-for-source` deletion and nonexistent source failures.
- `assertEmptyDir` verifies failed restore leaves target empty.

## Control Flow
Tests create temp data, snapshot it, list snapshots, execute deletion commands, and assert success/failure per scenario. Restore tests compare source and restored directories before deletion, then check snapshot-ID restore failure and root-ID restore success after maintenance.

## State And Persistence Behavior
Deletes snapshot manifests or snapshot metadata while content may remain recoverable by root object ID. Maintenance can garbage-collect unreachable content but deleted root IDs remain restorable in the tested path. All-source deletion changes multiple snapshot manifests for a source atomically from the user's perspective.

## Dependencies And Integration Points
Uses `testenv`, `clitestutil`, `testdirtree`, `testutil`, and shared `compareDirs`. Integrates manifest listing/removal, snapshot delete, restore, and maintenance.

## Risks And Edge Cases
The distinction between manifest ID, object ID, snapshot ID, and root object ID is subtle and security-sensitive. Output field parsing in `TestSnapshotDeleteTypeCheck` assumes `manifest ls` column ordering. Restore-after-delete behavior intentionally distinguishes snapshot manifest availability from content root recoverability.

## Test Signals
Strong signal for deletion safety, dry-run semantics, type checks, and post-delete recovery behavior.
