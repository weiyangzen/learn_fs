
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_copy_move_history_test.go

## Purpose
Verifies `snapshot copy-history` and `snapshot move-history` rewrite snapshot source identity across user, host, and path selectors while preserving snapshot counts.

## Important APIs, Types, And Functions
- `TestSnapshotCopy` creates two snapshots under `user1@host1`, copies history to another user on the same host, copies all host history to a new host, moves selected history to other host selectors, and copies a specific source path to another source path.
- `assertSnapshotCount` lists all snapshots with `-a` and checks exact counts per `snapshot.SourceInfo`.

## Control Flow
The test incrementally performs history copy/move commands and asserts the full expected source set after each step. It uses explicit `SourceInfo` maps to ensure no extra sources remain after move operations and no copies are missing after copy operations.

## State And Persistence Behavior
Snapshot metadata is duplicated or moved between source identities. Underlying object content is not the main concern; manifest source metadata and history grouping are the persisted state under test.

## Dependencies And Integration Points
Uses `testenv`, `clitestutil.ListSnapshotsAndExpectSuccess`, and `snapshot.SourceInfo`. Integrates CLI source selector parsing for `user@host`, `@host`, and `user@host:path` forms.

## Risks And Edge Cases
Source selector parsing is path-sensitive and can vary across platforms if paths contain separators or drive-like syntax. The test assumes copied histories keep exactly two snapshots and move operations remove the old selected source.

## Test Signals
Good regression signal for source history migration/copy features and selector parsing.
