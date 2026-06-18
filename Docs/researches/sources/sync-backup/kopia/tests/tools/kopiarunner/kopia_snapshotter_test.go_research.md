<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_test.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_test.go

This file unit-tests snapshot list parsing. `TestSnapListParse` feeds sample `snapshot list --all --manifest-id` output to `parseSnapshotListForSnapshotIDs` and verifies extracted manifest IDs.

The test isolates a fragile parser from the need for an executable. It covers empty input and representative output lines.

Risks not covered include changes in `manifest list` output, localized/altered CLI output, and duplicate or malformed manifest tokens. Integration tests supplement this parser test with real CLI output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/kopia_snapshotter_test.go -->
