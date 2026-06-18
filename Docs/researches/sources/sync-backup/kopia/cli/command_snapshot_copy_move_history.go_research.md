<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_copy_move_history.go -->
# sources/sync-backup/kopia/cli/command_snapshot_copy_move_history.go

## Purpose
Implements `snapshot copy-history` and `snapshot move-history`, used to preserve snapshot history when hostnames, usernames, or source paths change.

## Important APIs, Types, And Functions
Key APIs include `commandSnapshotCopyMoveHistory`, `setup`, `snapshotCopyMoveHelp`, `run`, `getCopySnapshotAction`, `getCopySourceAndDestination`, `snapshotExists`, `sameSnapshot`, and `getCopyDestination`.

## Control Flow
The command parses a source and optional destination, rejects destination username/path overrides that would collapse multiple source identities, lists source and destination snapshots, computes destination source info for each manifest, skips already matching destinations, saves copied manifests with a cleared ID, and deletes originals for move mode.

## State And Persistence Behavior
It mutates snapshot manifest metadata only. Copy creates new manifests pointing at existing root object IDs; move additionally deletes source manifests. Dry-run logs intended operations without writes.

## Dependencies And Integration Points
Depends on `snapshot.ParseSourceInfo`, snapshot listing/saving, repository writer deletion, and shared timestamp formatting.

## Risks And Edge Cases
The core risk is accidental history collapse or duplicate history if source/destination matching is too broad. `sameSnapshot` only compares start time and root object ID, so metadata differences are ignored for duplicate detection.

## Test Signals
Tests should cover the documented source/destination matrix, dry-run no-write behavior, duplicate detection, move deletion, and invalid destination path/user cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_copy_move_history.go -->
