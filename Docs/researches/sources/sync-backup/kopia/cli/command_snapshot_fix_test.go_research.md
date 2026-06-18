<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_fix_test.go

## Purpose
Exercises snapshot-fix workflows by creating snapshots, deliberately damaging repository content or selecting files, running repair commands, and inspecting resulting manifests and file maps.

## Important APIs, Types, And Functions
Important helpers include `TestSnapshotFix`, `forgetContents`, `mustGetContentMap`, `mustGetFileMap`, `mustListDirEntries`, and `mustWriteFileWithRepeatedData`. The tests use `testenv.CLITest`, content maps, snapshotfs roots, and directory entry collection.

## Control Flow
The test builds source trees with repeated data, creates snapshots, records object/content identifiers, removes or forgets content blobs to simulate invalid files, runs fix commands in dry-run and commit forms, and checks remaining files/manifests.

## State And Persistence Behavior
Persistent state under test includes repository content indexes/blobs, snapshot manifests, rewritten directory objects, and CLI-visible file presence after repair.

## Dependencies And Integration Points
Integrates CLI commands, snapshot upload, low-level content maps, blob deletion/forgetting, snapshotfs traversal, and test repository helpers.

## Risks And Edge Cases
Because it manipulates repository internals, it is sensitive to content packing/layout changes. Tests must distinguish missing file content from directory metadata damage and ensure cleanup helpers do not hide repair failures.

## Test Signals
Strong regression signal for invalid-file and remove-file behavior, especially commit semantics and resulting snapshot trees. It complements unit-level rewriter tests by going through the CLI.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_test.go -->
