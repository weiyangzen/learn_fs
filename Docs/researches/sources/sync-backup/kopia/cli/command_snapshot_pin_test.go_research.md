<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_pin_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_pin_test.go

## Purpose
Tests snapshot pinning behavior through the CLI and manifest inspection helpers.

## Important APIs, Types, And Functions
Defines `TestSnapshotPin` and `mustListSnapshots`. The test creates a repository, snapshots data, runs `snapshot pin` with add/remove operations, lists manifests, and checks pin sets.

## Control Flow
The control flow is end-to-end: create snapshots, read manifests, update pins by manifest or root ID, then reload snapshots to assert the persisted `Pins` field reflects requested changes and no-op cases behave correctly.

## State And Persistence Behavior
Persistent state under test is snapshot manifests in the temporary repository. The local filesystem is used only to create initial snapshot content.

## Dependencies And Integration Points
Integrates CLI commands, snapshot creation, snapshot listing APIs, and manifest pin update logic.

## Risks And Edge Cases
Assertions depend on manifest ordering and helper filtering. The test should keep covering both root ID and manifest ID addressing because they use different code paths.

## Test Signals
Strong signal for `command_snapshot_pin.go`; it complements retention tests by focusing on pin metadata persistence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_pin_test.go -->
