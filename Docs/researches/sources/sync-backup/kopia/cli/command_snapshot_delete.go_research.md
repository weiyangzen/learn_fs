<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_delete.go -->
# sources/sync-backup/kopia/cli/command_snapshot_delete.go

## Purpose
Implements snapshot deletion by manifest ID, root object ID, or all snapshots for a source, with explicit confirmation required for actual writes.

## Important APIs, Types, And Functions
Important functions are `run`, `snapshotDeleteSources`, `deleteSnapshot`, and `deleteSnapshotsByRootObjectID`. It uses `snapshot.LoadSnapshot`, `snapshot.ListSnapshotManifests`, `snapshot.FindSnapshotsByRootObjectID`, and `repo.DeleteManifest`.

## Control Flow
`run` dispatches to source deletion when `--all-snapshots-for-source` is set. Otherwise each provided ID is first treated as a manifest ID, then as a root object ID if the manifest is not found. `deleteSnapshot` logs dry-run output unless `--delete` was provided.

## State And Persistence Behavior
Persistent mutation is manifest deletion only; object content remains subject to repository maintenance/garbage collection. Dry-run leaves repository state unchanged.

## Dependencies And Integration Points
Integrates snapshot manifest loading/listing, object ID parsing, repository writer deletion, and timestamp formatting.

## Risks And Edge Cases
A root object ID can match multiple manifests, so confirmation text must be clear. Source deletion errors if no snapshots match. The hidden `--unsafe-ignore-source` alias maps to confirmation and is retained for compatibility.

## Test Signals
Tests should validate dry-run versus confirmed deletion, manifest ID and root ID paths, all-source deletion, invalid IDs, and no-match errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_delete.go -->
