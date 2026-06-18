<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_restore.go -->
# sources/sync-backup/kopia/cli/command_snapshot_restore.go

## Purpose
Provides the snapshot-specific restore command type by embedding the generic `commandRestore` implementation.

## Important APIs, Types, And Functions
The only type is `commandSnapshotRestore struct { commandRestore }`; behavior and flags are inherited from the shared restore command.

## Control Flow
Control flow is delegated entirely to embedded `commandRestore` setup/run methods when `command_snapshot.go` registers `restore.setup`.

## State And Persistence Behavior
Persistent behavior is inherited: restore writes files to the target filesystem and reads repository snapshot objects, but this wrapper adds no state.

## Dependencies And Integration Points
Integrates the snapshot command namespace with the shared restore implementation elsewhere in the CLI package.

## Risks And Edge Cases
Risk is mostly structural: changes to `commandRestore` must remain compatible with this embedded wrapper and the snapshot command registration.

## Test Signals
Tests for restore should exercise `snapshot restore` command invocation, while this file itself needs only compile/registration coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_restore.go -->
