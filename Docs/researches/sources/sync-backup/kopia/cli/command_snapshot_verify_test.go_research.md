<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_verify_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_verify_test.go

## Purpose
Tests snapshot verification behavior against intact and deliberately damaged repository content, including JSON verifier results.

## Important APIs, Types, And Functions
Defines `TestSnapshotVerify` and `unmarshalSnapVerify`. The test creates snapshots, removes or damages content through repository/test helpers, runs `snapshot verify` with different targets and `--json`, then validates `snapshotfs.VerifierResult` fields.

## Control Flow
Control flow exercises successful verification, missing data detection, verification by manifest ID, by source, by directory/file object ID, and JSON output parsing.

## State And Persistence Behavior
Persistent test state is a temporary repository with snapshots and manipulated content/blobs to simulate integrity failures.

## Dependencies And Integration Points
Integrates CLI verify command, snapshot creation, low-level repository mutation helpers, JSON output, and snapshotfs verifier result structures.

## Risks And Edge Cases
The test depends on predictable object/content IDs and verifier counters. Repository format changes can alter counts while the integrity signal remains useful.

## Test Signals
Strong signal for verifier target selection and JSON result shape. It should be kept aligned with any changes to verifier aggregation semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_verify_test.go -->
