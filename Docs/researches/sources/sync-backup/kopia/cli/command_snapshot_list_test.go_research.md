<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_list_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_list_test.go

## Purpose
Tests CLI snapshot listing output for basic long listing behavior and cases where the same file appears in multiple snapshots.

## Important APIs, Types, And Functions
Defines `TestSnapshotList` and `TestSnapshotListWithSameFileInMultipleSnapshots`, using in-process CLI repositories, temp directories, file mutations, and output line assertions.

## Control Flow
The tests create repository state, make snapshots, run `snapshot list`/`ls` with flags such as `-l`, and verify that output includes expected source paths, snapshot rows, and repeated-file behavior.

## State And Persistence Behavior
Persistent test state is a temporary filesystem repository with created snapshot manifests and local files used to generate those manifests.

## Dependencies And Integration Points
Integrates snapshot create and list commands, test environment helpers, local filesystem state, and text output formatting.

## Risks And Edge Cases
Like most CLI output tests, it is sensitive to line counts, timestamps, and wording. It exercises behavior through the full CLI rather than isolated list helpers.

## Test Signals
Useful as a regression signal for command aliases, row grouping, and identical/repeated output. It does not deeply cover JSON, tags, retention, or storage stats.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_list_test.go -->
