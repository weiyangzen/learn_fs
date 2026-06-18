<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_pin.go -->
# sources/sync-backup/kopia/cli/command_snapshot_pin.go

## Purpose
Implements `snapshot pin`, updating pin labels on snapshots to prevent or allow retention deletion.

## Important APIs, Types, And Functions
Defines `commandSnapshotPin`, `run`, `pinSnapshotsByRootObjectID`, and `pinSnapshot`. It uses manifest ID lookup first, root object ID fallback, `Manifest.UpdatePins`, and `snapshot.UpdateSnapshot`.

## Control Flow
The command requires at least one `--add` or `--remove` flag, then processes each ID. Each matched manifest is updated only if pins actually change; otherwise it logs a no-op.

## State And Persistence Behavior
Persistent state is the snapshot manifest's `Pins` field. Updating a snapshot writes a new/updated manifest record through snapshot APIs.

## Dependencies And Integration Points
Integrates repository writer actions, snapshot manifest loading, root-object reverse lookup, object ID parsing, and policy pin compaction logic inside `UpdatePins`.

## Risks And Edge Cases
A root object ID can update many manifests. Add/remove conflicts are resolved by `UpdatePins`, so caller expectations depend on that method. There is no dry-run flag.

## Test Signals
Tests should verify add, remove, no-op, multiple IDs, root-object matching, and retention interaction for pinned snapshots.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_pin.go -->
